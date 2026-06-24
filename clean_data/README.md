# clean_data/

Output of the **streaming pipeline** (`cybersec-slm run`): per-source cleaned
JSONL, written here as each source finishes fetch → convert → clean.

Layout mirrors `raw_data/`:

```
clean_data/
  <Sub-Domain>/
    <source>/
      <file>.jsonl     # records that passed all cleaning stages
```

Each record carries the standard fields (`source`, `url`, `license`, `text`,
plus source-specific keys). Records whose text was built from a non-`text`
column (e.g. a dataset's `question`/`answer` or `shortDescription`) also carry
`_text_field` recording where the text came from.

Pipeline flow that lands data here (see `src/cybersec_slm/extraction/parallel.py`
and `src/cybersec_slm/cleaning/pipeline.py`):

1. **fetch** the source → JSONL under `raw_data/`
2. **clean** it (text mapping → sanitize → anomaly → PII → language; per-source
   dedup disabled)
3. write the kept records here, then **delete that source's raw files**
4. after all sources finish, one **global dedup pass** removes cross-source
   duplicates in place

Companion trees (also generated, also git-ignored):

- `flagged/` — behavioral anomalies for human review
- `dropped/` — structural / dedup / language / feature-table drops, each
  annotated with a `_reason`
- `logs/clean_report.csv` — per-file counts (`mapped_text`, `excluded_no_text`,
  dups, `out`, …)

> The `.jsonl` contents are **generated and git-ignored** (they can be large).
> Only this README is tracked, so the folder exists after a fresh clone.
