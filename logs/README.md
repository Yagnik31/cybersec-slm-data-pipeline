# Logs

Collection logs and provenance, generated at runtime by the
[extraction](../extraction) pipeline:

- `pipeline.log` — rotating loguru debug log.
- `ingest_log.sqlite` — one row per produced/skipped file (provenance + final table).
- `final_table.csv` — exported summary (`python run.py table`).

Files here are generated and not checked in.
