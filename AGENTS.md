# Agent Instructions — a16z Chart Library

This repo already contains a full a16z.news scrape plus a classified image library.
Default behavior is conservative: preserve the existing `source/`, `graphs/`, and
`progress/` outputs, resume incrementally, and avoid broad rewrites unless the user
explicitly asks for them.

## Current Layout

```text
scripts/
  scrape.py
  reclassify.py
  reclass_all.py
  build_browse_html.py
  a16z_charts/
  examples/

progress/
  completed_articles.txt
  in_progress/
    <article-slug>.json

source/
  YYYY-MM/
    <article-slug>/
      index.html
      metadata.json
  unknown/
    <legacy-slug>/
      index.html
      metadata.json

graphs/
  browse.html
  area/
  bar/
  combo/
  infographic/
  line/
  map/
  other/
  pie/
  scatter/
  screenshot/
  table/
  title/
```

Notes:
- New article cache directories must go under `source/YYYY-MM/<slug>/`.
- Legacy `source/unknown/<slug>/` directories are preserved as historical cache and
  should not be moved unless the user explicitly asks for migration work.
- `graphs/browse.html` is generated output, but it is committed and should be rebuilt
  when the library changes.

## Task 1 — Scrape And Resume Safely

Single-process run:

```bash
source venv/bin/activate && python scripts/scrape.py
```

The scraper:
- crawls the full `https://www.a16z.news/sitemap.xml`
- downloads article HTML plus metadata
- classifies inline body images during scrape
- saves new article directories under `source/YYYY-MM/<slug>/`
- saves images into the top-level `graphs/` taxonomy
- records finished articles in `progress/completed_articles.txt`

### Finished manifest and restart behavior

`progress/completed_articles.txt` is the durable source of truth for finished
articles. One canonical article URL per line.

During an active scrape, each article also gets an ephemeral
`progress/in_progress/<slug>.json` marker. If the scraper restarts and finds a stale
marker for an article that is not in `progress/completed_articles.txt`, it must:

1. delete that article's partial `source/YYYY-MM/<slug>/` directory
2. delete that article's partial graph outputs for the same slug
3. remove the stale in-progress marker
4. retry the article from scratch

If an in-progress marker exists for an article that is already in the completed
manifest, the marker is stale and should be removed without deleting good outputs.

### Sharded runs

Prepare cleanup/manifest state once:

```bash
source venv/bin/activate && python scripts/scrape.py --prepare-manifest-only
```

Then launch 15 shards:

```bash
for i in $(seq 0 14); do
  source venv/bin/activate && python scripts/scrape.py --shard-index "$i" --shard-count 15 --skip-backfill
done
```

Rules:
- Do not launch sharded workers without the prep step.
- Do not delete finished `source/` or `graphs/` content.
- Only incomplete in-progress article outputs should be cleaned up.

## Task 2 — Classification

The current canonical library layout is the top-level `graphs/` taxonomy:

```text
bar line area pie scatter table combo map infographic title screenshot other
```

Important:
- Keep all image types. Do not drop title cards, screenshots, infographics, or other
  non-chart visuals.
- The scraper already classifies new images into the folders above.
- Broad reclassification is not part of the default workflow. Do not run it unless the
  user asks.

If the user explicitly wants to reclassify the ambiguous bucket only:

```bash
source venv/bin/activate && python scripts/reclassify.py
```

That script only reclassifies `graphs/other/` into:
`bar, line, area, pie, scatter, table, combo, map, infographic, title, screenshot, other`

`scripts/reclass_all.py` is a separate bulk-normalization utility that targets an
`other_v2/` structure. It is not the default current layout and should not be run
unless the user explicitly asks for that alternate organization.

## Task 3 — Browser

Regenerate the committed static browser with:

```bash
source venv/bin/activate && python scripts/build_browse_html.py
```

This writes `graphs/browse.html`.

Browser behavior:
- indexes only `graphs/`
- shows the directory structure in the sidebar
- opens a gallery for each leaf directory
- supports `Left` / `Right` to move between items
- supports `Up` / `Down` to move between leaf directories
- caps image preview height at `600px` and does not upscale smaller images
- filters likely preview-only assets such as tiny thumbnails and spacer strips when a
  real article-sized version exists

For graph images, the browser also surfaces article metadata and dynamic style data:
- publication date
- publication title
- style era
- style family
- title-card dimensions
- title-card palette
- dynamically detected style-shift threshold

That metadata is derived from the saved corpus at build time:
- article title/date from `source/.../index.html`
- style analysis from `graphs/title/`

If `source/` or `graphs/` changes, rebuild `graphs/browse.html`.

## Task 4 — Commit And Push

Typical commit flow:

```bash
git add AGENTS.md README.md scripts/ progress/ source/ graphs/
git commit -m "Update a16z chart library"
git push
```

Rules:
- Do not commit `.env`.
- `graphs/browse.html` is generated output and should be committed when regenerated.
- `progress/completed_articles.txt` is durable project state and should be committed
  when it changes.
- `progress/in_progress/` should normally be empty in a clean finished state.

## Environment

- Python 3.12
- venv at `./venv/`
- activate with `source venv/bin/activate`
- `OPENAI_API_KEY` and `MODEL=o4-mini` live in `.env`
- install dependencies with `pip install -r requirements.txt` if needed
- scraper throttling in `scripts/scrape.py` is intentional; do not remove it unless the
  user explicitly asks
