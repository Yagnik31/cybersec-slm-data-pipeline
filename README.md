# Cybersecurity SLM Data Pipeline

A pipeline to collect, clean, and consolidate cybersecurity text data for SLM training.

An installable package (`cybersec_slm`) with two stages — **extraction** (pull +
normalize sources to JSONL) and **cleaning** (sanitize → anomaly-check → dedup →
PII removal → language filter). EDA, schema normalization and CI are future work.

## Layout
```
src/cybersec_slm/
  core.py              shared: logger, optional-import loader, data paths, JSONL/hash
  cli.py               unified CLI (extract / clean / all)
  extraction/          common.py, fetch.py, scrape.py, scrape_html.py, manifest.py, run.py
  cleaning/            common.py, sanitize/anomaly/dedup/pii/langfilter, pipeline.py, run.py
tests/                 extraction/ + cleaning/ (pytest)
sources/  docs/        research notes and documentation
```
Generated at runtime (git-ignored): `raw_data/` (extraction output), `cleaned/`
(EDA handoff), `flagged/` (annotation), `dropped/` (audit), `logs/` (logs + reports).

## Setup
```bash
cp .env.example .env
uv venv && source .venv/bin/activate
uv sync                       # core (extraction) deps
uv sync --extra cleaning      # optional: upgrade cleaning stages to named tools
uv sync --extra dev           # optional: pytest + ruff
```

## Usage
Data paths resolve to the current directory (or `CYBERSEC_SLM_DATA_ROOT`):
```bash
cybersec-slm extract all      # -> raw_data/   (or: scrape | fetch | html | table)
cybersec-slm clean all        # raw_data/ -> cleaned/ flagged/ dropped/ + report
cybersec-slm all              # extract, then clean
# equivalently: python -m cybersec_slm <stage> ...
```

## Develop
```bash
pytest          # run the test suite
ruff check src tests
```

## Progress
- Week 1: sources researched, licensing verified, shortlist confirmed.
- Week 2: extraction + cleaning stages implemented and packaged (`src/` layout, CLI, tests).
- Next: EDA, schema normalization, CI automation.