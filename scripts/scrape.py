#!/usr/bin/env python3
"""
Crawl https://www.a16z.news/ for article images.

- Downloads articles into ./source/YYYY-MM/<slug>/
- Tracks completed articles in ./progress/completed_articles.txt
- Tracks restart markers in ./progress/in_progress/
- Classifies each body image with OpenAI o4-mini vision and saves to ./graphs/<type>/

Reads config from .env:
  OPENAI_API_KEY  — required
  MODEL           — defaults to o4-mini
"""

import os
import sys
import json
import time
import re
import base64
import tempfile
import argparse
import hashlib
import subprocess
import shutil
import fcntl
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

load_dotenv(REPO_ROOT / ".env")

DOMAIN = "https://www.a16z.news"
SITEMAP_URL = f"{DOMAIN}/sitemap.xml"
SOURCE_DIR = REPO_ROOT / "source"
GRAPHS_DIR = REPO_ROOT / "graphs"
PROGRESS_DIR = REPO_ROOT / "progress"
COMPLETED_FILE = PROGRESS_DIR / "completed_articles.txt"
IN_PROGRESS_DIR = PROGRESS_DIR / "in_progress"
IMAGE_TYPES = [
    "bar",
    "line",
    "area",
    "pie",
    "scatter",
    "table",
    "combo",
    "map",
    "infographic",
    "title",
    "screenshot",
    "other",
]
MODEL = os.getenv("MODEL", "o4-mini")
DELAY_ARTICLE = 1.0   # seconds between article fetches
DELAY_IMAGE = 0.5     # seconds between image downloads

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; a16z-chart-library/1.0; +research)"
}


def repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape and classify images from a16z.news.")
    parser.add_argument("--shard-index", type=int, default=0, help="0-based shard index for parallel runs.")
    parser.add_argument("--shard-count", type=int, default=1, help="Total shard count for parallel runs.")
    parser.add_argument(
        "--skip-backfill",
        action="store_true",
        help="Skip legacy cache backfill into completed_articles.txt.",
    )
    parser.add_argument(
        "--prepare-manifest-only",
        action="store_true",
        help="Backfill completed_articles.txt, clean stale in-progress work, and exit.",
    )
    args = parser.parse_args()
    if args.shard_count < 1:
        parser.error("--shard-count must be at least 1")
    if args.shard_index < 0 or args.shard_index >= args.shard_count:
        parser.error("--shard-index must be between 0 and --shard-count - 1")
    if args.shard_count > 1 and not args.skip_backfill and not args.prepare_manifest_only:
        parser.error(
            "Run --prepare-manifest-only once before launching shards, then use "
            "--skip-backfill for each sharded worker."
        )
    return args


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def check_env():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("ERROR: OPENAI_API_KEY is not set.")
        print("Add it to .env or export it in your shell.")
        sys.exit(1)
    print(f"Model: {MODEL}")
    return key


def setup_dirs():
    SOURCE_DIR.mkdir(exist_ok=True)
    PROGRESS_DIR.mkdir(exist_ok=True)
    COMPLETED_FILE.touch(exist_ok=True)
    IN_PROGRESS_DIR.mkdir(exist_ok=True)
    GRAPHS_DIR.mkdir(exist_ok=True)
    for t in IMAGE_TYPES:
        (GRAPHS_DIR / t).mkdir(exist_ok=True)


def canonicalize_article_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        return url.strip()
    path = parsed.path.rstrip("/") or parsed.path
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def load_completed_articles() -> set[str]:
    if not COMPLETED_FILE.exists():
        return set()
    return {
        canonicalize_article_url(line)
        for line in COMPLETED_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def slug_in_completed_articles(slug: str, completed_articles: set[str]) -> bool:
    return any(slug_from_url(url) == slug for url in completed_articles)


def build_legacy_cache() -> tuple[dict[str, dict[str, Path | str | None]], set[str]]:
    cached = {}
    slugs_without_url = set()
    legacy_root = SOURCE_DIR / "unknown"
    if not legacy_root.exists():
        return cached, slugs_without_url

    for article_dir in sorted(legacy_root.iterdir()):
        if not article_dir.is_dir():
            continue
        slug = article_dir.name
        entry = cached.setdefault(slug, {"dir": article_dir, "url": None})
        meta_path = article_dir / "metadata.json"
        if not meta_path.exists():
            slugs_without_url.add(slug)
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            slugs_without_url.add(slug)
            continue
        url = meta.get("url")
        if url:
            entry["url"] = canonicalize_article_url(url)
        else:
            slugs_without_url.add(slug)
    return cached, slugs_without_url


def append_completed_article(url: str, completed_articles: set[str]):
    canonical_url = canonicalize_article_url(url)
    if canonical_url in completed_articles:
        return
    with COMPLETED_FILE.open("a+", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        fh.seek(0)
        existing = {
            canonicalize_article_url(line)
            for line in fh.read().splitlines()
            if line.strip()
        }
        if canonical_url not in existing:
            fh.seek(0, os.SEEK_END)
            fh.write(f"{canonical_url}\n")
            fh.flush()
            os.fsync(fh.fileno())
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    completed_articles.add(canonical_url)


def marker_path_for_slug(slug: str) -> Path:
    return IN_PROGRESS_DIR / f"{slug}.json"


def write_json_atomic(path: Path, data: dict) -> None:
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f"{path.name}.",
        suffix=".tmp",
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        Path(tmp_name).replace(path)
    except Exception:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def safe_resolve(path_str: str | None) -> Path | None:
    if not path_str:
        return None
    try:
        return Path(path_str).resolve()
    except Exception:
        return None


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def build_in_progress_marker(url: str, slug: str, article_dir: Path, image_count: int) -> dict:
    return {
        "url": canonicalize_article_url(url),
        "slug": slug,
        "article_dir": str(article_dir),
        "graph_basenames": [f"{slug}-{idx}.png" for idx in range(1, image_count + 1)],
        "created_at": int(time.time()),
    }


def write_in_progress_marker(url: str, slug: str, article_dir: Path, image_count: int) -> Path:
    marker_path = marker_path_for_slug(slug)
    write_json_atomic(marker_path, build_in_progress_marker(url, slug, article_dir, image_count))
    return marker_path


def remove_in_progress_marker(marker_path: Path) -> None:
    marker_path.unlink(missing_ok=True)


def load_in_progress_marker(marker_path: Path) -> dict | None:
    if not marker_path.exists():
        return None
    try:
        return json.loads(marker_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Could not read in-progress marker {marker_path.name}: {e}")
        return None


def iter_slug_graph_matches(slug: str, graph_basenames: list[str] | None = None) -> list[Path]:
    matches = []
    seen = set()
    basenames = graph_basenames or []
    for basename in basenames:
        for path in GRAPHS_DIR.rglob(basename):
            if path.is_file() and path not in seen:
                matches.append(path)
                seen.add(path)
    for pattern in (f"{slug}-*.png", f"{slug}-*.jpg", f"{slug}-*.jpeg"):
        for path in GRAPHS_DIR.rglob(pattern):
            if path.is_file() and path not in seen:
                matches.append(path)
                seen.add(path)
    return matches


def iter_article_dirs_for_slug(slug: str) -> list[Path]:
    matches = []
    for candidate in sorted(SOURCE_DIR.glob(f"*/{slug}")):
        if candidate.parent.name in {"unknown", "in_progress"}:
            continue
        if candidate.is_dir():
            matches.append(candidate)
    return matches


def cleanup_interrupted_article(marker_path: Path, completed_articles: set[str]) -> str:
    marker = load_in_progress_marker(marker_path)
    marker = marker or {}
    canonical_url = canonicalize_article_url(str(marker.get("url", "")))
    slug = str(marker.get("slug") or marker_path.stem)

    if (canonical_url and canonical_url in completed_articles) or slug_in_completed_articles(slug, completed_articles):
        remove_in_progress_marker(marker_path)
        return "removed stale marker for completed article"

    article_dir = safe_resolve(marker.get("article_dir"))
    if article_dir and is_within(article_dir, SOURCE_DIR) and article_dir.exists():
        shutil.rmtree(article_dir)
    for candidate in iter_article_dirs_for_slug(slug):
        if article_dir and candidate.resolve() == article_dir:
            continue
        shutil.rmtree(candidate)

    graph_basenames = marker.get("graph_basenames")
    if not isinstance(graph_basenames, list):
        graph_basenames = []
    for graph_path in iter_slug_graph_matches(slug, graph_basenames):
        if is_within(graph_path, GRAPHS_DIR):
            graph_path.unlink(missing_ok=True)

    remove_in_progress_marker(marker_path)
    return "deleted incomplete article outputs for retry"


def cleanup_stale_in_progress(completed_articles: set[str]) -> dict[str, int]:
    stats = {"removed_completed_markers": 0, "restarted_articles": 0, "unreadable_markers": 0}
    for marker_path in sorted(IN_PROGRESS_DIR.glob("*.json")):
        result = cleanup_interrupted_article(marker_path, completed_articles)
        if result == "removed stale marker for completed article":
            stats["removed_completed_markers"] += 1
        elif result == "deleted incomplete article outputs for retry":
            stats["restarted_articles"] += 1
        else:
            stats["unreadable_markers"] += 1
    return stats


def backfill_completed_articles(
    completed_articles: set[str],
    legacy_cached_articles: dict[str, dict[str, Path | str | None]],
) -> int:
    missing = []
    for entry in legacy_cached_articles.values():
        url = entry.get("url")
        if url and url not in completed_articles:
            missing.append(url)

    if not missing:
        return 0

    existing_lines = []
    if COMPLETED_FILE.exists():
        existing_lines = COMPLETED_FILE.read_text(encoding="utf-8").splitlines()

    fd, tmp_name = tempfile.mkstemp(
        dir=str(PROGRESS_DIR),
        prefix=f"{COMPLETED_FILE.name}.",
        suffix=".tmp",
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for line in existing_lines:
                fh.write(f"{line}\n")
            for url in missing:
                fh.write(f"{url}\n")
        Path(tmp_name).replace(COMPLETED_FILE)
    except Exception:
        Path(tmp_name).unlink(missing_ok=True)
        raise

    completed_articles.update(missing)
    return len(missing)


# ---------------------------------------------------------------------------
# Step 1: Enumerate articles from sitemap
# ---------------------------------------------------------------------------

def get_article_urls():
    print(f"Fetching sitemap: {SITEMAP_URL}")
    resp = requests.get(SITEMAP_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "lxml-xml")
    urls = []
    for loc in soup.find_all("loc"):
        url = loc.text.strip()
        if "/p/" in url:
            urls.append(url)
    print(f"Found {len(urls)} article URLs")
    return urls


def select_shard_urls(article_urls: list[str], shard_index: int, shard_count: int) -> list[str]:
    if shard_count == 1:
        return article_urls

    selected = []
    for url in article_urls:
        digest = hashlib.sha256(canonicalize_article_url(url).encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:8], "big") % shard_count
        if bucket == shard_index:
            selected.append(url)
    return selected


# ---------------------------------------------------------------------------
# Step 2 & 3: Fetch article, extract images, save to source/
# ---------------------------------------------------------------------------

def slug_from_url(url):
    path = urlparse(url).path  # e.g. /p/some-article-slug
    return path.rstrip("/").split("/")[-1]


def get_publish_date(soup):
    """Extract YYYY-MM from article metadata."""
    meta = soup.find("meta", property="article:published_time")
    if meta and meta.get("content"):
        return meta["content"][:7]  # YYYY-MM
    time_tag = soup.find("time")
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"][:7]
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        value = find_structured_date(data)
        if value:
            return value[:7]
    return "unknown"


def find_structured_date(node):
    if isinstance(node, dict):
        for key in ("datePublished", "dateCreated"):
            value = node.get(key)
            if isinstance(value, str) and len(value) >= 7:
                return value
        for value in node.values():
            found = find_structured_date(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_structured_date(item)
            if found:
                return found
    return None


def extract_body_images(soup):
    """
    Return substackcdn image URLs from the article body.
    Skips header/thumbnail images.
    """
    body = soup.find("div", class_="available-content")
    if not body:
        body = soup.find("article")
    if not body:
        return []

    imgs = []
    for img in body.find_all("img"):
        src = img.get("src", "")
        if "substackcdn.com" in src and "/fetch/" in src:
            # Strip query params for full-res URL
            clean = re.sub(r"\?.*$", "", src)
            if clean not in imgs:
                imgs.append(clean)

    return imgs


def save_article(article_dir: Path, url: str, html: str, pub_date: str, image_urls: list):
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "index.html").write_text(html, encoding="utf-8")
    meta = {
        "url": url,
        "published": pub_date,
        "image_urls": image_urls,
    }
    (article_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Step 4: Download + classify images with OpenAI o4-mini vision
# ---------------------------------------------------------------------------

def download_image(url: str) -> bytes | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"    [WARN] Failed to download {url}: {e}")
        return None


def is_svg_asset(url: str, image_bytes: bytes) -> bool:
    if url.lower().endswith(".svg"):
        return True
    head = image_bytes[:512].lstrip().lower()
    return head.startswith(b"<?xml") or b"<svg" in head


def rasterize_svg(image_bytes: bytes) -> bytes | None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        src = temp_dir / "image.svg"
        dest = temp_dir / "image.png"
        src.write_bytes(image_bytes)
        result = subprocess.run(
            ["sips", "-s", "format", "png", str(src), "--out", str(dest)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not dest.exists():
            stderr = result.stderr.strip()
            if stderr:
                print(f"    [WARN] Could not rasterize SVG: {stderr}")
            else:
                print("    [WARN] Could not rasterize SVG")
            return None
        return dest.read_bytes()


def classify_image(client: OpenAI, image_bytes: bytes) -> tuple[str | None, bool]:
    """
    Ask o4-mini to classify the image.
    Returns (category, had_error).
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.standard_b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"    [WARN] Could not process image: {e}")
        return None, True

    prompt = (
        "Look at this image carefully and classify it into exactly one category.\n\n"
        "Choose from: bar, line, area, pie, scatter, table, combo, map, "
        "infographic, title, screenshot, other.\n\n"
        "Use other for photos, illustrations, logos, avatars, decorative images, "
        "or anything that does not fit the named categories.\n\n"
        "Reply with one word only. No explanation."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_completion_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        result = response.choices[0].message.content.strip().lower()
        if result in IMAGE_TYPES:
            return result, False
        for t in IMAGE_TYPES:
            if t in result:
                return t, False
        return "other", False
    except Exception as e:
        print(f"    [WARN] OpenAI API error: {e}")
        return None, True


def find_existing_graph(slug: str, idx: int) -> Path | None:
    filename = f"{slug}-{idx}.png"
    matches = sorted(path for path in GRAPHS_DIR.glob(f"*/{filename}") if path.is_file())
    return matches[0] if matches else None


def save_graph(image_bytes: bytes, chart_type: str, slug: str, idx: int):
    filename = f"{slug}-{idx}.png"
    dest = GRAPHS_DIR / chart_type / filename
    if dest.exists():
        return True
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.save(dest, format="PNG")
        return True
    except Exception as e:
        print(f"    [WARN] Could not save image {filename}: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    api_key = check_env()
    setup_dirs()
    completed_articles = load_completed_articles()
    legacy_cached_articles, legacy_slugs_without_url = build_legacy_cache()
    backfilled = 0
    if not args.skip_backfill:
        backfilled = backfill_completed_articles(completed_articles, legacy_cached_articles)
    cleanup_stats = {"removed_completed_markers": 0, "restarted_articles": 0, "unreadable_markers": 0}
    if not args.skip_backfill or args.prepare_manifest_only:
        cleanup_stats = cleanup_stale_in_progress(completed_articles)
    if backfilled:
        print(f"Backfilled {backfilled} completed article URLs into {repo_rel(COMPLETED_FILE)}")
    print(f"Loaded {len(completed_articles)} completed article URLs")
    if legacy_slugs_without_url:
        print(f"Found {len(legacy_slugs_without_url)} legacy cache directories without metadata URLs")
    if cleanup_stats["removed_completed_markers"]:
        print(
            "Removed "
            f"{cleanup_stats['removed_completed_markers']} stale in-progress markers for completed articles"
        )
    if cleanup_stats["restarted_articles"]:
        print(
            "Deleted partial outputs for "
            f"{cleanup_stats['restarted_articles']} interrupted articles"
        )
    if cleanup_stats["unreadable_markers"]:
        print(
            "Removed "
            f"{cleanup_stats['unreadable_markers']} unreadable in-progress markers"
        )
    if args.prepare_manifest_only:
        print("Prepared completion manifest only")
        return
    client = OpenAI(api_key=api_key)

    article_urls = get_article_urls()
    article_urls = select_shard_urls(article_urls, args.shard_index, args.shard_count)
    print(
        f"Shard {args.shard_index + 1}/{args.shard_count} "
        f"assigned {len(article_urls)} article URLs"
    )

    stats = {
        "scanned": 0,
        "with_images": 0,
        "skipped_no_images": 0,
        "skipped_completed": 0,
        "incomplete_articles": 0,
        "errors": 0,
        "images_by_type": {t: 0 for t in IMAGE_TYPES},
    }

    for i, url in enumerate(article_urls, 1):
        canonical_url = canonicalize_article_url(url)
        slug = slug_from_url(canonical_url)
        marker_path = marker_path_for_slug(slug)
        print(f"\n[{i}/{len(article_urls)}] {slug}")

        if marker_path.exists():
            result = cleanup_interrupted_article(marker_path, completed_articles)
            print(f"  Restart cleanup — {result}")

        if canonical_url in completed_articles:
            print("  Completed — skipping")
            stats["skipped_completed"] += 1
            continue

        if slug in legacy_slugs_without_url:
            print("  Legacy cache without metadata URL — skipping")
            stats["skipped_completed"] += 1
            continue

        try:
            resp = requests.get(canonical_url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            print(f"  [ERROR] {e}")
            stats["errors"] += 1
            time.sleep(DELAY_ARTICLE)
            continue

        soup = BeautifulSoup(html, "lxml")
        image_urls = extract_body_images(soup)
        pub_date = get_publish_date(soup)
        if pub_date == "unknown":
            print("  [ERROR] Could not determine publish month — article not saved")
            stats["errors"] += 1
            time.sleep(DELAY_ARTICLE)
            continue

        article_dir = SOURCE_DIR / pub_date / slug
        write_in_progress_marker(canonical_url, slug, article_dir, len(image_urls))
        try:
            save_article(article_dir, canonical_url, html, pub_date, image_urls)
        except Exception as e:
            print(f"  [ERROR] Could not save article files: {e}")
            stats["errors"] += 1
            time.sleep(DELAY_ARTICLE)
            continue
        print(f"  Saved article → {repo_rel(article_dir)}/ ({len(image_urls)} images)")
        time.sleep(DELAY_ARTICLE)

        stats["scanned"] += 1

        if not image_urls:
            append_completed_article(canonical_url, completed_articles)
            remove_in_progress_marker(marker_path)
            stats["skipped_no_images"] += 1
            print("  No body images — marked complete")
            continue

        had_image_errors = False
        for j, img_url in enumerate(image_urls, 1):
            existing_graph = find_existing_graph(slug, j)
            if existing_graph:
                print(f"  Image {j}/{len(image_urls)}: existing ({existing_graph.parent.name})")
                continue

            print(f"  Image {j}/{len(image_urls)}: ", end="", flush=True)
            image_bytes = download_image(img_url)
            time.sleep(DELAY_IMAGE)
            if not image_bytes:
                print("download failed")
                had_image_errors = True
                continue
            if is_svg_asset(img_url, image_bytes):
                png_bytes = rasterize_svg(image_bytes)
                if not png_bytes:
                    print("svg rasterization failed")
                    had_image_errors = True
                    continue
                image_bytes = png_bytes

            chart_type, classify_error = classify_image(client, image_bytes)
            if classify_error:
                print("classification failed")
                had_image_errors = True
                continue
            print(chart_type)

            if not save_graph(image_bytes, chart_type, slug, j):
                had_image_errors = True
                continue
            stats["images_by_type"][chart_type] += 1

        stats["with_images"] += 1
        if had_image_errors:
            print("  [WARN] Article had image errors — leaving incomplete for retry")
            stats["incomplete_articles"] += 1
            continue

        append_completed_article(canonical_url, completed_articles)
        remove_in_progress_marker(marker_path)
        print("  Marked complete")

    # Summary
    print("\n" + "=" * 50)
    print("DONE")
    print(f"Articles scanned:       {stats['scanned']}")
    print(f"Articles with images:   {stats['with_images']}")
    print(f"Skipped completed:      {stats['skipped_completed']}")
    print(f"Skipped (no images):    {stats['skipped_no_images']}")
    print(f"Incomplete articles:    {stats['incomplete_articles']}")
    print(f"Errors:                 {stats['errors']}")
    print("Images saved by type:")
    for t, n in stats["images_by_type"].items():
        if n:
            print(f"  {t:10s}: {n}")
    total = sum(stats["images_by_type"].values())
    print(f"  {'TOTAL':10s}: {total}")


if __name__ == "__main__":
    main()
