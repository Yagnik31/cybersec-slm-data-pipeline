# Discovery — search-engine source discovery

`cybersec-slm discover` finds **new** candidate cybersecurity sources by querying
a search engine with per–Sub-Domain keyword sets, maps each hit into the
finalized tracking sheet's row schema, drops anything already in the sheet, and
appends the survivors back to the Google Sheet.

It's the inverse of [`extraction/sources.py`](../extraction/sources.py): that
module *reads* the sheet to drive ingestion; this one *grows* the sheet.

## Flow

```
for each Sub-Domain (optionally filtered with --domains):
  for each keyword in that domain:
    Google Programmable Search  ->  results
    for each result:
      assign Sub-Domain (keyword's domain, refined by snippet vocab)
      infer Category + Original Format from the URL/host
      drop if the link already exists in the sheet, or was seen this run
write survivors to logs/discovered/discovered-YYYYMMDD.csv (always)
append survivors to the live sheet               (unless --dry-run)
```

Domain assignment is **keyword sets + snippet fallback**: a result keeps the
Sub-Domain of the keyword that found it unless another domain's vocabulary
(`keywords.DOMAIN_VOCAB`) scores *strictly higher* on its title+snippet.

## Which columns get filled

The sheet has 16 columns (see `row.SHEET_COLUMNS`). Only what's knowable at
discovery time is filled — extraction-dependent fields are left blank on
purpose:

| Filled at discovery | Left blank (extraction / human) |
|---|---|
| Name, Sub-Domain, Description, Dataset Link | File Count, Original/JSONL Size, Total Lines |
| Category, Original Format, Date Added | License, Last Updated, Verified?, Uploaded?, Note |

`Name` is the HF/GitHub owner for those hosts, else the cleaned page title.
`Description` is the search snippet (trimmed). `Category`/`Original Format` come
from the URL shape (`huggingface…/datasets` → Dataset, `github.com` → Repository,
`.pdf` → Document/PDF, else Website/HTML).

## Credentials

| Purpose | Variable | Notes |
|---|---|---|
| Search | `GOOGLE_API_KEY` | API key with the **Custom Search API** enabled |
| Search | `GOOGLE_CSE_ID` | Programmable Search Engine id (`cx`), set to search the whole web |
| Append | `GOOGLE_SHEETS_CREDENTIALS` | path to a **service-account** JSON key with edit access to the sheet |

Dedup reads the sheet through its public CSV export, so `--dry-run` needs **no**
Google credentials at all — only `GOOGLE_API_KEY`/`GOOGLE_CSE_ID` for the search.
The live append needs the `discovery` extra (`uv sync --extra discovery`) and
the service account shared as an editor on the sheet.

## Usage

```bash
# Dry run: discover, dedup, write the CSV — never touch the sheet.
cybersec-slm discover --dry-run

# One domain, cap how many new rows it keeps.
cybersec-slm discover --domains "Malware Analysis" --max-per-domain 10

# Live: append new rows to the finalized sheet (default sheet URL is built in).
cybersec-slm discover

# Point at a different sheet / tune fan-out.
cybersec-slm discover --sheet-url <url> --per-keyword 8
```

The local CSV under `logs/discovered/` is written on every run (live or dry) as
a reviewable record of exactly what was added.
