# a16z Chart Library

Crawls [a16z.news](https://www.a16z.news/) for article images, downloads the source articles, and organizes body images by type using OpenAI o4-mini vision classification.

## What it does

1. **Enumerates** all articles from the site's sitemap
2. **Downloads** article HTML and metadata into `source/YYYY-MM/<slug>/`
3. **Tracks** completed article URLs in `source/completed_articles.txt` so reruns never re-download finished work
4. **Tracks** in-progress work in `source/in_progress/` so interrupted articles can be deleted and retried cleanly
5. **Classifies** each body image with OpenAI o4-mini vision
6. **Saves** images into `graphs/` organized by type

## Output structure

```
source/
  completed_articles.txt
  in_progress/
    <article-slug>.json  # ephemeral restart marker for incomplete articles
  YYYY-MM/
    <article-slug>/
      index.html        # full article HTML
      metadata.json     # url, publish date, image URLs

graphs/
  bar/
  line/
  area/
  pie/
  scatter/
  table/
  combo/
  map/
  infographic/
  title/
  screenshot/
  other/
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your key, or edit `.env` directly:

```
OPENAI_API_KEY=sk-proj-...
MODEL=o4-mini
```

## Usage

```bash
python scrape.py
```

The script prints progress as it runs and a summary at the end. `source/completed_articles.txt`
is the durable finished-manifest, and `source/in_progress/<slug>.json` marks an article that
started but did not finish. On restart, any article with an in-progress marker and no completed
manifest entry is deleted and re-scraped from scratch.

Legacy cached articles under `source/unknown/` are preserved and backfilled into the completion
manifest on startup.

For a 15-way sharded run, prepare the manifest and cleanup state once, then launch workers with
`--skip-backfill`:

```bash
python scrape.py --prepare-manifest-only
python scrape.py --shard-index 0 --shard-count 15 --skip-backfill
python scrape.py --shard-index 1 --shard-count 15 --skip-backfill
# ...through shard 14
```

## Requirements

- Python 3.12+
- `OPENAI_API_KEY` in `.env` — used to classify images with `o4-mini`
