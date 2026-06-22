# Raw data

Collected raw data in JSONL, produced by the [extraction](../extraction)
pipeline. Layout:

```
raw_data/
  <Sub-Domain>/            e.g. Cryptography, Cloud Security, Threat Intelligence
    <source>/
      <source>.jsonl       normalized records (one JSON object per line)
      <source>.<ext>       original download (csv/json/pdf/parquet/...)
      _SOURCE.json         provenance for scraped PDFs/feeds/sites
```

Record schema (scraped sources): `{source, url, license, page?, text}`.
Dataset (hf/kaggle/url) records keep their original columns.

This folder is the output target; files here are generated and not checked in.
