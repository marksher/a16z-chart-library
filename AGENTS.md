# Agent Instructions — a16z Chart Library

Two tasks: (1) finish scraping all articles, (2) reclassify every image into a clean
two-tier folder structure using `scripts/reclass_all.py`.

---

## Task 1 — Finish scraping articles

```bash
source venv/bin/activate && python scripts/scrape.py
```

Crawls every article URL from `https://www.a16z.news/sitemap.xml` (~170 total).
`progress/completed_articles.txt` is the finished-articles manifest: if a canonical
article URL is in that file, the article is complete and must be skipped.

During an active scrape, each article also gets an ephemeral
`progress/in_progress/<slug>.json` marker. If the scraper restarts and finds a stale
in-progress marker for an article that is not in `progress/completed_articles.txt`, it
must delete that article's partial `source/YYYY-MM/<slug>/` directory and any partial
graph files for that slug, then restart the article from scratch.

Single-process runs are safe to resume with:

```bash
source venv/bin/activate && python scripts/scrape.py
```

For highest-throughput runs, prepare the manifest/cleanup state once and then launch
15 shards:

```bash
source venv/bin/activate && python scripts/scrape.py --prepare-manifest-only
for i in $(seq 0 14); do
  source venv/bin/activate && python scripts/scrape.py --shard-index "$i" --shard-count 15 --skip-backfill
done
```

Do not launch sharded workers without the prep step. Preserve all existing finished
`source/` and `graphs/` content; only incomplete in-progress article outputs should be
deleted on restart.

---

## Task 2 — Reclassify all images into clean two-tier structure

```bash
source venv/bin/activate && python scripts/reclass_all.py
```

Re-examines every image in `graphs/` with o4-mini vision (15 parallel threads).
Sorts into this structure:

```
graphs/
  bar/           ← pure bar/column charts only
  line/          ← pure line charts only
  area/          ← pure area/stacked area only
  pie/           ← pie/donut only
  scatter/       ← scatter, bubble, dumbbell
  table/         ← data tables only
  map/           ← geographic maps only
  other_v2/
    combo/       ← dual-axis or mixed-type charts
    infographic/ ← designed multi-element visuals
    title/       ← title cards, banners, decorative images
    screenshot/  ← app/website/UI screenshots
    other/       ← anything that doesn't fit above
```

### Classification rules
| o4-mini returns | Destination |
|---|---|
| bar / line / area / pie / scatter / table / map | `graphs/<type>/` |
| combo | `graphs/other_v2/combo/` |
| infographic | `graphs/other_v2/infographic/` |
| title | `graphs/other_v2/title/` |
| screenshot | `graphs/other_v2/screenshot/` |
| other or anything else | `graphs/other_v2/other/` |

### Coordination files (written during the run)
| File | Purpose |
|---|---|
| `progress/.queue.txt` | Master list of all images (written once at start) |
| `progress/.in_progress.txt` | Appended as each image starts processing |
| `progress/.done.txt` | Appended as each image finishes (old, file, new, action) |

Run is resumable: if interrupted, delete `.queue.txt` to trigger a fresh scan,
or leave it and re-run — images already in the right place are a no-op move.

### Verification
- `wc -l progress/.done.txt` should equal total image count when done
- `graphs/combo/`, `graphs/infographic/`, `graphs/screenshot/`, `graphs/title/`
  should be empty after the run (all contents moved to `other_v2/`)

---

## Task 3 — Commit and push

```bash
git add AGENTS.md README.md scripts/ progress/ source/ graphs/
git commit -m "Scrape all articles and reclassify all images into two-tier structure"
git push
```

Do **not** commit `.env`.

---

## Environment

- Python 3.12, venv at `./venv/`
- Activate: `source venv/bin/activate`
- `OPENAI_API_KEY` and `MODEL=o4-mini` are in `.env` (loaded automatically)
- Install deps if needed: `pip install -r requirements.txt`
- Rate limiting: `scrape.py` has 1s/article and 0.5s/image delays — do not remove
