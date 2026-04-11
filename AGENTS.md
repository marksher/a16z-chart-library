# Agent Instructions — a16z Chart Library

Two tasks: scrape all articles from a16z.news and classify the chart images by type.

## Task 1 — Scrape articles

```bash
source venv/bin/activate && python scrape.py
```

Crawls https://www.a16z.news/ (~170 articles total). For each article that contains
inline images, saves the HTML to `source/<slug>/` and downloads the images.
Already-downloaded articles are skipped automatically — safe to resume.

## Task 2 — Reclassify `graphs/other/`

After scraping finishes:

```bash
source venv/bin/activate && python reclassify.py
```

Re-classifies everything in `graphs/other/` into specific types:
`bar, line, area, pie, scatter, table, combo, map, infographic, title, screenshot`

## Task 3 — Commit and push

```bash
git add source/ graphs/
git commit -m "Scrape all articles and classify charts by type"
git push
```

Do **not** commit `.env`.

## Environment

- Python 3.12, venv at `./venv/`
- `OPENAI_API_KEY` and `MODEL=o4-mini` are in `.env` (loaded automatically)
- All dependencies installed — run `pip install -r requirements.txt` if needed
