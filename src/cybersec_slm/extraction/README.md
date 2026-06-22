# Extraction

Scripts that pull cybersecurity text data from each source and normalize it to
JSONL under [`../raw_data`](../raw_data). Provenance for every produced/skipped
file is recorded in a SQLite ingest log under [`../logs`](../logs).

## Modules
| File | Purpose |
|---|---|
| `common.py` | Extraction helpers: HTTP (httpx + tenacity), robust readers (pandas + json-repair), JSONL conversion, and the SQLite `IngestLog`. Shared logger/paths/hashing come from `cybersec_slm.core`. |
| `manifest.py` | Catalog of sources: `DATASETS` (hf/kaggle/github/url), `PDFS`, `FEEDS`, `SITES`. |
| `fetch.py` | Dataset fetcher — one handler per kind (hf, kaggle, github, url). |
| `scrape.py` | PDFs (PyMuPDF, one record per page) and JSON feeds (httpx + orjson). |
| `scrape_html.py` | Crawls robots.txt-permitted sites (selectolax; Playwright for JS pages). |
| `run.py` | Orchestrator + final-table reporter (`run(cmd)` / `main()`). |

## Paths
Resolved by `cybersec_slm.core` from `CYBERSEC_SLM_DATA_ROOT` (default: current
directory):

- raw data  → `raw_data/<Sub-Domain>/<source>/*.jsonl`
- logs      → `logs/pipeline.log`
- ingest db → `logs/ingest_log.sqlite`
- table     → `logs/final_table.csv`

## Usage
```bash
cybersec-slm extract scrape   # PDFs + feeds
cybersec-slm extract fetch    # datasets in manifest.DATASETS
cybersec-slm extract html     # crawl manifest.SITES
cybersec-slm extract all      # scrape, fetch, then crawl
cybersec-slm extract table    # print final table + write logs/final_table.csv
```

## Notes
- A 5 GB cap (`common.CAP_BYTES`) guards both downloads and produced JSONL;
  oversized files are skipped but still recorded in the log.
- Kaggle sources need credentials (`~/.kaggle/kaggle.json` or the
  `KAGGLE_USERNAME` / `KAGGLE_KEY` environment variables).
- `scrape_html.py`'s JS path needs the Playwright browser: `playwright install chromium`.
- Record schema produced by scrapers: `{source, url, license, page?, text}`.
