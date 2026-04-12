#!/usr/bin/env python3
"""
Generate a single static HTML browser at graphs/browse.html for the current
graphs/ tree.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = REPO_ROOT / "graphs" / "browse.html"
ROOT_NAMES = ("graphs",)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
TEXT_SUFFIXES = {".json", ".txt", ".md"}
STRIP_MAX_HEIGHT = 120
SMALL_PREVIEW_MAX_WIDTH = 400
SMALL_PREVIEW_MAX_HEIGHT = 400
FULL_SIZE_MIN_WIDTH = 1000
FULL_SIZE_MIN_HEIGHT = 700
DATE_INPUT_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f%z",
)
MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def tree_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def browse_href(path: Path) -> str:
    return os.path.relpath(path, OUTPUT_FILE.parent).replace(os.sep, "/")


def normalize_datetime(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().replace("Z", "+00:00")


def normalize_month(value: str | None) -> str | None:
    if not value:
        return None
    if MONTH_PATTERN.match(value.strip()):
        return value.strip()

    normalized = normalize_datetime(value)
    for fmt in DATE_INPUT_FORMATS:
        try:
            parsed = datetime.strptime(normalized, fmt)
            return parsed.strftime("%Y-%m")
        except ValueError:
            continue

    if len(value) >= 10:
        try:
            parsed = datetime.strptime(value[:10], "%Y-%m-%d")
            return parsed.strftime("%Y-%m")
        except ValueError:
            return None
    return None


def format_published_date(value: str | None, fallback_month: str | None = None) -> str | None:
    if value:
        normalized = normalize_datetime(value)
        for fmt in DATE_INPUT_FORMATS:
            try:
                parsed = datetime.strptime(normalized, fmt)
                return parsed.strftime("%B %-d, %Y")
            except ValueError:
                continue
        if len(value) >= 10:
            try:
                parsed = datetime.strptime(value[:10], "%Y-%m-%d")
                return parsed.strftime("%B %-d, %Y")
            except ValueError:
                pass
    if fallback_month:
        try:
            parsed = datetime.strptime(fallback_month, "%Y-%m")
            return parsed.strftime("%B %Y")
        except ValueError:
            return fallback_month
    return None


def image_size(path: Path) -> tuple[int, int] | None:
    try:
        with Image.open(path) as img:
            return img.size
    except Exception:
        return None


def average_rgb(path: Path) -> tuple[int, int, int] | None:
    try:
        with Image.open(path) as img:
            sample = img.convert("RGB").resize((1, 1))
            rgb = sample.getpixel((0, 0))
            return int(rgb[0]), int(rgb[1]), int(rgb[2])
    except Exception:
        return None


def rgb_hex(rgb: tuple[int, int, int] | None) -> str | None:
    if not rgb:
        return None
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def image_slug(path: Path) -> str | None:
    stem = path.stem
    if "-" not in stem:
        return None
    slug, suffix = stem.rsplit("-", 1)
    return slug if suffix.isdigit() else None


def image_index(path: Path) -> int:
    stem = path.stem
    if "-" not in stem:
        return 10_000
    suffix = stem.rsplit("-", 1)[-1]
    return int(suffix) if suffix.isdigit() else 10_000


def select_primary_title_card(slug: str, preview_paths: set[Path]) -> Path | None:
    title_dir = REPO_ROOT / "graphs" / "title"
    candidates = []
    for path in sorted(title_dir.glob(f"{slug}-*")):
        if not path.is_file() or path in preview_paths or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        size = image_size(path)
        if not size:
            continue
        rank = (
            0 if image_index(path) == 1 else 1,
            0 if size[1] > STRIP_MAX_HEIGHT and size[0] > SMALL_PREVIEW_MAX_WIDTH else 1,
            -(size[0] * size[1]),
            image_index(path),
            path.name,
        )
        candidates.append((rank, path))

    return min(candidates)[1] if candidates else None


def classify_title_family(size: tuple[int, int], rgb: tuple[int, int, int]) -> str:
    width, height = size
    r, g, b = rgb
    avg = (r + g + b) / 3
    aspect = width / max(height, 1)

    if aspect >= 3.0 and height <= 260:
        if r >= g + 20 and r >= b + 20:
            return "Warm Banner"
        if g >= r + 15 and b >= r + 20:
            return "Cool Banner"
        return "Compact Banner"

    if avg >= 205:
        return "Light Minimal Card"

    if b >= g >= r and (g - r) >= 18 and (b - r) >= 35:
        return "Teal Series Card"

    if max(rgb) - min(rgb) <= 18 and avg <= 70:
        return "Dark Neutral Card"

    if b > g > r and 48 <= r <= 82 and 68 <= g <= 96:
        return "Core Slate Card"

    if width >= FULL_SIZE_MIN_WIDTH and height >= 500:
        return "Expanded Card Variant"

    return "Mixed Variant"


def build_title_card_index(preview_paths: set[Path]) -> dict[str, dict]:
    title_cards = {}
    for title_path in sorted((REPO_ROOT / "graphs" / "title").glob("*")):
        if not title_path.is_file() or title_path in preview_paths:
            continue
        slug = image_slug(title_path)
        if not slug or slug in title_cards:
            continue

        primary = select_primary_title_card(slug, preview_paths)
        if not primary:
            continue

        size = image_size(primary)
        rgb = average_rgb(primary)
        if not size or not rgb:
            continue

        title_cards[slug] = {
            "style_family": classify_title_family(size, rgb),
            "style_palette": rgb_hex(rgb),
            "style_dimensions": f"{size[0]}x{size[1]}",
            "title_card_path": tree_path(primary),
            "title_card_href": browse_href(primary),
        }

    return title_cards


def parse_article_fields(article_dir: Path, metadata: dict) -> dict | None:
    index_path = article_dir / "index.html"
    if not index_path.exists():
        return None

    title = None
    published_value = None
    try:
        soup = BeautifulSoup(index_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    except Exception:
        return None

    for selector in (
        ('meta[property="og:title"]', "content"),
        ('meta[name="twitter:title"]', "content"),
        ("h1.post-title", None),
        ("h1", None),
    ):
        node = soup.select_one(selector[0])
        if not node:
            continue
        title = node.get(selector[1], "").strip() if selector[1] else node.get_text(" ", strip=True)
        if title:
            break

    for selector in (
        ('meta[property="article:published_time"]', "content"),
        ("time[datetime]", "datetime"),
    ):
        node = soup.select_one(selector[0])
        if not node:
            continue
        published_value = node.get(selector[1], "").strip()
        if published_value:
            break

    if not published_value:
        for script in soup.find_all("script", type="application/ld+json"):
            raw = script.string or script.get_text()
            if not raw:
                continue
            match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', raw)
            if match:
                published_value = match.group(1).strip()
                break

    published = format_published_date(published_value, metadata.get("published"))
    if not title and not published:
        return None

    return {
        "title": title,
        "published": published,
        "published_month": normalize_month(published_value),
    }


def detect_style_threshold(article_index: dict[str, dict]) -> dict:
    family_counts = Counter(
        article["style_family"]
        for article in article_index.values()
        if article.get("style_family")
    )
    dominant_family = family_counts.most_common(1)[0][0] if family_counts else None

    by_month: dict[str, list[str]] = defaultdict(list)
    for article in article_index.values():
        month = article.get("published_month")
        family = article.get("style_family")
        if month and family:
            by_month[month].append(family)

    threshold_month = None
    if dominant_family:
        for month in sorted(by_month):
            families = by_month[month]
            if len(families) < 5:
                continue
            month_counts = Counter(families)
            dominant_share = month_counts.get(dominant_family, 0) / len(families)
            if len(month_counts) >= 2 and dominant_share < 0.75:
                threshold_month = month
                break

    return {
        "dominant_family": dominant_family,
        "threshold_month": threshold_month,
        "threshold_label": format_published_date(None, threshold_month),
    }


def build_article_index(preview_paths: set[Path]) -> tuple[dict[str, dict], dict]:
    title_card_index = build_title_card_index(preview_paths)
    candidates: dict[str, tuple[int, dict]] = {}
    for metadata_path in REPO_ROOT.glob("source/*/*/metadata.json"):
        article_dir = metadata_path.parent
        slug = article_dir.name
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        article = parse_article_fields(article_dir, metadata) or {}
        article["url"] = metadata.get("url")
        article["published_month"] = normalize_month(metadata.get("published")) or article.get("published_month")
        article["published"] = article.get("published") or format_published_date(None, article.get("published_month"))
        if not article.get("title"):
            article["title"] = slug.replace("-", " ").title()
        article.update(title_card_index.get(slug, {}))

        score = 0
        if article.get("title"):
            score += 2
        if article.get("published"):
            score += 1
        if article.get("style_family"):
            score += 1
        if article_dir.parent.name != "unknown":
            score += 2

        existing = candidates.get(slug)
        if not existing or score >= existing[0]:
            candidates[slug] = (score, article)

    article_index = {slug: article for slug, (_, article) in candidates.items()}
    style_analysis = detect_style_threshold(article_index)

    threshold_month = style_analysis.get("threshold_month")
    for article in article_index.values():
        month = article.get("published_month")
        if threshold_month and month:
            article["style_era"] = "Expanded System" if month >= threshold_month else "Anchored System"
        elif article.get("style_family") and not threshold_month:
            article["style_era"] = "Anchored System"
        if style_analysis.get("threshold_label"):
            article["style_threshold"] = style_analysis["threshold_label"]

    return article_index, style_analysis


def collect_preview_images() -> set[Path]:
    graph_root = REPO_ROOT / "graphs"
    by_slug: dict[str, list[tuple[Path, int, int]]] = {}

    for path in graph_root.rglob("*"):
        if not path.is_file() or path == OUTPUT_FILE or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        slug = image_slug(path)
        if not slug:
            continue
        size = image_size(path)
        if not size:
            continue
        by_slug.setdefault(slug, []).append((path, size[0], size[1]))

    preview_paths: set[Path] = set()
    for items in by_slug.values():
        has_full_size = any(
            width >= FULL_SIZE_MIN_WIDTH or height >= FULL_SIZE_MIN_HEIGHT
            for _, width, height in items
        )
        for path, width, height in items:
            if height <= STRIP_MAX_HEIGHT:
                preview_paths.add(path)
                continue
            if has_full_size and width <= SMALL_PREVIEW_MAX_WIDTH and height <= SMALL_PREVIEW_MAX_HEIGHT:
                preview_paths.add(path)

    return preview_paths


def file_sort_key(path: Path) -> tuple[int, str]:
    priority = {
        "index.html": 0,
        "index.htm": 0,
        "metadata.json": 1,
    }
    return (priority.get(path.name, 2), path.name.lower())


def build_item(path: Path, article_index: dict[str, dict]) -> dict:
    suffix = path.suffix.lower()
    item = {
        "name": path.name,
        "path": tree_path(path),
        "href": browse_href(path),
        "kind": "file",
    }
    if suffix in IMAGE_SUFFIXES:
        item["kind"] = "image"
        slug = image_slug(path)
        if slug and slug in article_index:
            item["article"] = article_index[slug]
    elif suffix in {".html", ".htm"}:
        item["kind"] = "html"
    elif suffix in TEXT_SUFFIXES:
        item["kind"] = "text"
        item["content"] = path.read_text(encoding="utf-8", errors="replace")
    return item


def build_tree(path: Path, preview_paths: set[Path], article_index: dict[str, dict]) -> dict:
    children = sorted([child for child in path.iterdir() if child.is_dir()], key=lambda p: p.name.lower())
    node = {
        "name": path.name,
        "path": tree_path(path),
    }
    if not children:
        items = [
            build_item(file_path, article_index)
            for file_path in sorted(path.iterdir(), key=file_sort_key)
            if file_path.is_file() and file_path not in preview_paths
        ]
        node["leaf"] = True
        node["items"] = items
        node["item_count"] = len(items)
        node["leaf_count"] = 1
        return node

    built_children = [build_tree(child, preview_paths, article_index) for child in children]
    node["leaf"] = False
    node["children"] = built_children
    node["leaf_count"] = sum(child["leaf_count"] for child in built_children)
    return node


def build_data() -> dict:
    roots = []
    preview_paths = collect_preview_images()
    article_index, style_analysis = build_article_index(preview_paths)
    for name in ROOT_NAMES:
        root_path = REPO_ROOT / name
        if root_path.exists():
            roots.append(build_tree(root_path, preview_paths, article_index))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "style_analysis": style_analysis,
        "roots": roots,
    }


def render_html(data: dict) -> str:
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>a16z Chart Library Browser</title>
  <style>
    :root {{
      --bg: #f4f1e8;
      --panel: #fffaf0;
      --panel-2: #f0ead8;
      --line: #d2c7ac;
      --text: #1d1a14;
      --muted: #726754;
      --accent: #8a3b12;
      --accent-soft: #f3d6bf;
      --shadow: 0 18px 60px rgba(70, 53, 31, 0.12);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(138, 59, 18, 0.08), transparent 28%),
        linear-gradient(180deg, #faf6ec 0%, var(--bg) 100%);
      min-height: 100vh;
    }}
    .shell {{
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      min-height: 100vh;
    }}
    .sidebar {{
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255, 250, 240, 0.95), rgba(240, 234, 216, 0.96));
      padding: 20px 18px 32px;
      overflow: auto;
    }}
    .content {{
      padding: 24px;
      overflow: auto;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.05;
      letter-spacing: -0.03em;
    }}
    .subhead {{
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }}
    .analysis-note {{
      margin: 0 0 18px;
      padding: 12px 14px;
      border: 1px solid rgba(138, 59, 18, 0.14);
      border-radius: 14px;
      background: rgba(255, 247, 235, 0.88);
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}
    .tree {{
      display: grid;
      gap: 10px;
    }}
    details {{
      border-left: 1px solid var(--line);
      padding-left: 12px;
      margin-left: 4px;
    }}
    details.root {{
      border-left: none;
      padding-left: 0;
      margin-left: 0;
    }}
    summary {{
      cursor: pointer;
      list-style: none;
      font-weight: 600;
      padding: 4px 0;
    }}
    summary::-webkit-details-marker {{
      display: none;
    }}
    summary::before {{
      content: "▸";
      display: inline-block;
      width: 1em;
      color: var(--accent);
      transition: transform 120ms ease;
    }}
    details[open] > summary::before {{
      transform: rotate(90deg);
    }}
    .branch-label {{
      display: inline-flex;
      align-items: baseline;
      gap: 8px;
    }}
    .count {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.02em;
    }}
    .leaf-button {{
      width: 100%;
      margin: 5px 0;
      border: 1px solid transparent;
      border-radius: 12px;
      background: transparent;
      color: inherit;
      text-align: left;
      padding: 9px 12px;
      cursor: pointer;
      font: inherit;
      transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
    }}
    .leaf-button:hover {{
      background: rgba(138, 59, 18, 0.08);
      border-color: rgba(138, 59, 18, 0.18);
    }}
    .leaf-button.active {{
      background: var(--accent-soft);
      border-color: rgba(138, 59, 18, 0.28);
      transform: translateX(2px);
    }}
    .leaf-path {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-top: 2px;
      word-break: break-word;
    }}
    .panel {{
      background: rgba(255, 250, 240, 0.92);
      border: 1px solid rgba(210, 199, 172, 0.9);
      border-radius: 24px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .panel-header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: end;
      padding: 20px 24px 16px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255, 247, 235, 0.98), rgba(247, 240, 225, 0.98));
    }}
    .eyebrow {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }}
    .title {{
      margin: 0;
      font-size: 24px;
      line-height: 1.15;
      word-break: break-word;
    }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
      text-align: right;
      white-space: nowrap;
    }}
    .controls {{
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 14px 24px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 250, 240, 0.82);
      flex-wrap: wrap;
    }}
    .button {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: white;
      color: var(--text);
      padding: 8px 14px;
      cursor: pointer;
      font: inherit;
    }}
    .button:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}
    .button:disabled {{
      opacity: 0.4;
      cursor: default;
      color: var(--muted);
      border-color: var(--line);
    }}
    .hint {{
      color: var(--muted);
      font-size: 13px;
      margin-left: auto;
    }}
    .item-strip {{
      display: flex;
      gap: 8px;
      padding: 16px 24px 0;
      overflow: auto;
      scrollbar-width: thin;
    }}
    .item-chip {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.75);
      padding: 7px 12px;
      cursor: pointer;
      white-space: nowrap;
      font: inherit;
      font-size: 13px;
    }}
    .item-chip.active {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }}
    .viewer {{
      padding: 20px 24px 24px;
    }}
    .viewer-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }}
    .viewer-path {{
      font-size: 15px;
      font-weight: 600;
      word-break: break-word;
    }}
    .viewer-link a {{
      color: var(--accent);
      text-decoration: none;
      font-size: 13px;
    }}
    .viewer-link a:hover {{
      text-decoration: underline;
    }}
    .article-meta {{
      display: none;
      margin-bottom: 14px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255, 251, 243, 0.95);
    }}
    .article-meta.visible {{
      display: block;
    }}
    .article-date {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }}
    .article-title {{
      font-size: 18px;
      line-height: 1.25;
      font-weight: 700;
      word-break: break-word;
    }}
    .article-facts {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    .fact-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border: 1px solid rgba(138, 59, 18, 0.16);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.85);
      font-size: 12px;
      line-height: 1;
      color: var(--text);
      white-space: nowrap;
    }}
    .fact-swatch {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      border: 1px solid rgba(29, 26, 20, 0.18);
      flex: 0 0 auto;
    }}
    .stage {{
      background: rgba(243, 236, 222, 0.65);
      border: 1px solid var(--line);
      border-radius: 20px;
      min-height: 68vh;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .stage iframe,
    .stage pre,
    .stage .placeholder {{
      width: 100%;
      min-height: 68vh;
      align-self: stretch;
    }}
    .stage img {{
      width: auto;
      height: auto;
      min-height: 0;
      max-width: 100%;
      max-height: 600px;
      display: block;
      align-self: center;
      background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(244,241,232,0.9));
    }}
    .stage iframe {{
      border: 0;
      background: white;
    }}
    .stage pre {{
      margin: 0;
      padding: 20px;
      overflow: auto;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 13px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .placeholder {{
      display: grid;
      place-items: center;
      color: var(--muted);
      padding: 24px;
      text-align: center;
    }}
    @media (max-width: 980px) {{
      .shell {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        max-height: 42vh;
        border-right: none;
        border-bottom: 1px solid var(--line);
      }}
      .content {{
        padding: 18px;
      }}
      .panel-header {{
        padding: 18px;
      }}
      .controls,
      .item-strip,
      .viewer {{
        padding-left: 18px;
        padding-right: 18px;
      }}
      .hint {{
        width: 100%;
        margin-left: 0;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <h1>a16z Library Browser</h1>
      <p class="subhead">
        Directory tree on the left, leaf-folder gallery on the right.
        Use <strong>Left</strong>/<strong>Right</strong> for items and
        <strong>Up</strong>/<strong>Down</strong> for sibling leaf folders.
      </p>
      <p id="analysis-note" class="analysis-note"></p>
      <div id="tree" class="tree"></div>
    </aside>
    <main class="content">
      <section class="panel">
        <div class="panel-header">
          <div>
            <div class="eyebrow">Static Browser</div>
            <h2 id="panel-title" class="title">Choose a leaf directory</h2>
          </div>
          <div id="panel-meta" class="meta">Generated {data["generated_at"]}</div>
        </div>
        <div class="controls">
          <button id="prev-dir" class="button">Previous Directory</button>
          <button id="prev-item" class="button">Previous Item</button>
          <button id="next-item" class="button">Next Item</button>
          <button id="next-dir" class="button">Next Directory</button>
          <div id="dir-status" class="hint"></div>
        </div>
        <div id="item-strip" class="item-strip"></div>
        <div class="viewer">
          <div class="viewer-head">
            <div id="viewer-path" class="viewer-path"></div>
            <div id="viewer-link" class="viewer-link"></div>
          </div>
          <div id="article-meta" class="article-meta"></div>
          <div id="stage" class="stage">
            <div class="placeholder">Select a leaf directory to browse its files.</div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script id="tree-data" type="application/json">{payload}</script>
  <script>
    const data = JSON.parse(document.getElementById("tree-data").textContent);
    const treeEl = document.getElementById("tree");
    const analysisNoteEl = document.getElementById("analysis-note");
    const itemStripEl = document.getElementById("item-strip");
    const panelTitleEl = document.getElementById("panel-title");
    const panelMetaEl = document.getElementById("panel-meta");
    const dirStatusEl = document.getElementById("dir-status");
    const viewerPathEl = document.getElementById("viewer-path");
    const viewerLinkEl = document.getElementById("viewer-link");
    const articleMetaEl = document.getElementById("article-meta");
    const stageEl = document.getElementById("stage");
    const prevDirEl = document.getElementById("prev-dir");
    const nextDirEl = document.getElementById("next-dir");
    const prevItemEl = document.getElementById("prev-item");
    const nextItemEl = document.getElementById("next-item");

    const leafOrder = [];
    const leafMap = new Map();
    const leafButtons = new Map();
    let currentLeafPath = null;
    let currentItemIndex = 0;

    function displayCountLabel(label, count, noun) {{
      return `${{label}} (${{count}} ${{noun}}${{count === 1 ? "" : "s"}})`;
    }}

    function openAncestors(element) {{
      let parent = element.parentElement;
      while (parent) {{
        if (parent.tagName === "DETAILS") {{
          parent.open = true;
        }}
        parent = parent.parentElement;
      }}
    }}

    function renderTreeNode(node, parentEl, depth) {{
      if (node.leaf) {{
        leafOrder.push(node.path);
        leafMap.set(node.path, node);

        const button = document.createElement("button");
        button.className = "leaf-button";
        button.dataset.path = node.path;
        button.innerHTML = `
          <strong>${{node.name}}</strong>
          <span class="leaf-path">${{node.path}}</span>
          <span class="count">${{node.item_count}} file${{node.item_count === 1 ? "" : "s"}}</span>
        `;
        button.addEventListener("click", () => selectLeaf(node.path));
        leafButtons.set(node.path, button);
        parentEl.appendChild(button);
        return;
      }}

      const details = document.createElement("details");
      details.className = depth === 0 ? "root" : "";
      details.open = depth === 0 || node.name === "graphs";

      const summary = document.createElement("summary");
      summary.innerHTML = `
        <span class="branch-label">
          <span>${{node.name}}</span>
          <span class="count">${{node.leaf_count}} leaf${{node.leaf_count === 1 ? "" : "s"}}</span>
        </span>
      `;
      details.appendChild(summary);

      const container = document.createElement("div");
      node.children.forEach((child) => renderTreeNode(child, container, depth + 1));
      details.appendChild(container);
      parentEl.appendChild(details);
    }}

    function renderTree() {{
      data.roots.forEach((root) => renderTreeNode(root, treeEl, 0));
    }}

    function renderAnalysisNote() {{
      const analysis = data.style_analysis || null;
      if (!analysis || !analysis.threshold_label || !analysis.dominant_family) {{
        analysisNoteEl.textContent = "Dynamic style analysis updates when the underlying graph set changes.";
        return;
      }}
      analysisNoteEl.textContent =
        `Dynamic title-style shift detected around ${{analysis.threshold_label}}. ` +
        `Dominant early family: ${{analysis.dominant_family}}.`;
    }}

    function getCurrentLeaf() {{
      return currentLeafPath ? leafMap.get(currentLeafPath) : null;
    }}

    function setActiveButton(path) {{
      leafButtons.forEach((button, candidate) => {{
        button.classList.toggle("active", candidate === path);
      }});
      const button = leafButtons.get(path);
      if (button) {{
        openAncestors(button);
        button.scrollIntoView({{block: "nearest"}});
      }}
    }}

    function renderStage(item) {{
      stageEl.textContent = "";
      if (!item) {{
        const empty = document.createElement("div");
        empty.className = "placeholder";
        empty.textContent = "This directory has no files to preview.";
        stageEl.appendChild(empty);
        return;
      }}

      if (item.kind === "image") {{
        const img = document.createElement("img");
        img.src = item.href;
        img.alt = item.name;
        stageEl.appendChild(img);
        return;
      }}

      if (item.kind === "html") {{
        const iframe = document.createElement("iframe");
        iframe.src = item.href;
        iframe.loading = "lazy";
        stageEl.appendChild(iframe);
        return;
      }}

      if (item.kind === "text") {{
        const pre = document.createElement("pre");
        pre.textContent = item.content || "";
        stageEl.appendChild(pre);
        return;
      }}

      const placeholder = document.createElement("div");
      placeholder.className = "placeholder";
      placeholder.innerHTML = `No inline preview for <strong>${{item.name}}</strong>.`;
      stageEl.appendChild(placeholder);
    }}

    function renderArticleMeta(item) {{
      articleMetaEl.textContent = "";
      articleMetaEl.classList.remove("visible");
      if (!item || item.kind !== "image" || !item.article) {{
        return;
      }}

      const bits = [];
      if (item.article.published) {{
        bits.push(`<div class="article-date">${{item.article.published}}</div>`);
      }}
      if (item.article.title) {{
        bits.push(`<div class="article-title">${{item.article.title}}</div>`);
      }}
      const facts = [];
      if (item.article.style_era) {{
        facts.push(`<span class="fact-pill">Era: ${{item.article.style_era}}</span>`);
      }}
      if (item.article.style_family) {{
        facts.push(`<span class="fact-pill">Style: ${{item.article.style_family}}</span>`);
      }}
      if (item.article.style_dimensions) {{
        facts.push(`<span class="fact-pill">Title card: ${{item.article.style_dimensions}}</span>`);
      }}
      if (item.article.style_palette) {{
        facts.push(
          `<span class="fact-pill"><span class="fact-swatch" style="background:${{item.article.style_palette}}"></span>` +
          `Palette: ${{item.article.style_palette}}</span>`
        );
      }}
      if (item.article.style_threshold) {{
        facts.push(`<span class="fact-pill">Shift: ${{item.article.style_threshold}}</span>`);
      }}
      if (facts.length) {{
        bits.push(`<div class="article-facts">${{facts.join("")}}</div>`);
      }}
      if (!bits.length) {{
        return;
      }}
      articleMetaEl.innerHTML = bits.join("");
      articleMetaEl.classList.add("visible");
    }}

    function renderItems(leaf) {{
      itemStripEl.textContent = "";
      leaf.items.forEach((item, index) => {{
        const chip = document.createElement("button");
        chip.className = "item-chip";
        chip.textContent = item.name;
        chip.classList.toggle("active", index === currentItemIndex);
        chip.addEventListener("click", () => {{
          currentItemIndex = index;
          renderViewer();
        }});
        itemStripEl.appendChild(chip);
      }});
    }}

    function renderViewer() {{
      const leaf = getCurrentLeaf();
      if (!leaf) {{
        panelTitleEl.textContent = "Choose a leaf directory";
        panelMetaEl.textContent = `Generated ${{data.generated_at}}`;
        dirStatusEl.textContent = "";
        viewerPathEl.textContent = "";
        viewerLinkEl.textContent = "";
        articleMetaEl.textContent = "";
        articleMetaEl.classList.remove("visible");
        itemStripEl.textContent = "";
        renderStage(null);
        prevDirEl.disabled = true;
        nextDirEl.disabled = true;
        prevItemEl.disabled = true;
        nextItemEl.disabled = true;
        return;
      }}

      if (currentItemIndex >= leaf.items.length) {{
        currentItemIndex = Math.max(leaf.items.length - 1, 0);
      }}
      if (currentItemIndex < 0) {{
        currentItemIndex = 0;
      }}

      const leafIndex = leafOrder.indexOf(leaf.path);
      const item = leaf.items[currentItemIndex] || null;

      panelTitleEl.textContent = leaf.path;
      panelMetaEl.textContent = displayCountLabel("Leaf directory", leaf.item_count, "file");
      dirStatusEl.textContent = `Directory ${{leafIndex + 1}} of ${{leafOrder.length}}`;
      viewerPathEl.textContent = item
        ? `${{item.path}} · item ${{currentItemIndex + 1}} of ${{Math.max(leaf.items.length, 1)}}`
        : "No previewable files";
      viewerLinkEl.innerHTML = item
        ? `<a href="${{item.href}}" target="_blank" rel="noopener">Open ${{item.name}}</a>`
        : "";

      prevDirEl.disabled = leafIndex <= 0;
      nextDirEl.disabled = leafIndex === -1 || leafIndex >= leafOrder.length - 1;
      prevItemEl.disabled = currentItemIndex <= 0;
      nextItemEl.disabled = leaf.items.length === 0 || currentItemIndex >= leaf.items.length - 1;

      renderItems(leaf);
      renderArticleMeta(item);
      renderStage(item);
    }}

    function selectLeaf(path) {{
      if (!leafMap.has(path)) {{
        return;
      }}
      currentLeafPath = path;
      currentItemIndex = 0;
      setActiveButton(path);
      renderViewer();
    }}

    function moveDirectory(offset) {{
      const leaf = getCurrentLeaf();
      if (!leaf) {{
        if (leafOrder.length) {{
          selectLeaf(leafOrder[0]);
        }}
        return;
      }}
      const currentIndex = leafOrder.indexOf(leaf.path);
      const nextIndex = currentIndex + offset;
      if (nextIndex >= 0 && nextIndex < leafOrder.length) {{
        selectLeaf(leafOrder[nextIndex]);
      }}
    }}

    function moveItem(offset) {{
      const leaf = getCurrentLeaf();
      if (!leaf || !leaf.items.length) {{
        return;
      }}
      const nextIndex = currentItemIndex + offset;
      if (nextIndex >= 0 && nextIndex < leaf.items.length) {{
        currentItemIndex = nextIndex;
        renderViewer();
      }}
    }}

    prevDirEl.addEventListener("click", () => moveDirectory(-1));
    nextDirEl.addEventListener("click", () => moveDirectory(1));
    prevItemEl.addEventListener("click", () => moveItem(-1));
    nextItemEl.addEventListener("click", () => moveItem(1));

    window.addEventListener("keydown", (event) => {{
      const tag = document.activeElement && document.activeElement.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") {{
        return;
      }}
      if (event.key === "ArrowLeft") {{
        event.preventDefault();
        moveItem(-1);
      }} else if (event.key === "ArrowRight") {{
        event.preventDefault();
        moveItem(1);
      }} else if (event.key === "ArrowUp") {{
        event.preventDefault();
        moveDirectory(-1);
      }} else if (event.key === "ArrowDown") {{
        event.preventDefault();
        moveDirectory(1);
      }}
    }});

    renderAnalysisNote();
    renderTree();
    if (leafOrder.length) {{
      selectLeaf(leafOrder[0]);
    }} else {{
      renderViewer();
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(render_html(build_data()), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
