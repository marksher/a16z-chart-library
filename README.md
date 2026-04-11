# a16z Chart Library

Crawls [a16z.news](https://www.a16z.news/) for data charts and graphs, downloads the source articles, and organizes images by chart type using Claude vision classification.

## What it does

1. **Enumerates** all articles from the site's sitemap (~175 articles)
2. **Downloads** articles that contain inline images into `source/`
3. **Classifies** each image with Claude vision — is it a chart? what kind?
4. **Saves** charts into `graphs/` organized by type

## Output structure

```
source/
  YYYY-MM/
    <article-slug>/
      index.html        # full article HTML
      metadata.json     # url, publish date, image URLs

graphs/
  bar/                  # bar charts
  line/                 # line/area charts
  pie/                  # pie/donut charts
  scatter/              # scatter plots
  table/                # data tables
  other/                # charts that don't fit the above
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scrape.py
```

The script prints progress as it runs and a summary at the end. It resumes safely if interrupted — already-downloaded articles are skipped on re-run.

## Requirements

- Python 3.12+
- `ANTHROPIC_API_KEY` — used to classify images with `claude-opus-4-6`
