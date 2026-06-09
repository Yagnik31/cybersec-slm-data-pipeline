# CyberSec SLM Data Pipeline

## Overview
An end-to-end data collection pipeline that sources, extracts, cleans, and consolidates raw cybersecurity text data for Small Language Model (SLM) training.

The pipeline covers four stages across four weeks:
- Week 1: Source discovery, licensing analysis, and pipeline planning
- Week 2: Raw data extraction, deduplication, and unified storage
- Week 3: Quality filtering, cleaning, and dataset statistics
- Week 4: Dataset freeze, data card, and handoff

---

## Team

| Name | Track | Responsibility |
|------|-------|----------------|
| Yagnik | Technical Setup + Docs | Repo structure, storage schema, reports |
| Vaibhav | Source Discovery + Licensing | Source hunting, licensing verification, scoring |
| Neil | Research Support + Validation | Source research support, test runs, risk register |

---

## Repo Structure

```
cybersec-slm-data-pipeline/
│
├── sources/
│   └── source_registry.csv
│
├── extraction/
│   └── README.md
│
├── raw_data/
│   └── README.md
│
├── logs/
│   └── README.md
│
├── docs/
│   ├── source_acceptance_criteria.md
│   ├── risk_register.md
│   └── week1_report.md
│
└── README.md
```

---

## Data Domain

Cybersecurity text across nine categories:

1. Attacks — techniques, incidents, case studies
2. Attack Prevention — controls, hardening, best practices
3. Code — malware samples, security tools, PoC exploits
4. Vulnerabilities — CVEs, advisories, disclosures
5. Policies — NIST, ISO standards, frameworks
6. Compliance Reports — audits, assessments, certifications
7. Articles, News, Blogs — threat intelligence, commentary
8. Scraping Techniques — data collection methodology
9. Other Python Libraries — security-relevant tooling documentation

---

## Output Format

| Stage | Format | Details |
|-------|--------|---------|
| Raw extract | JSONL | One record per document, flexible schema |
| Deduplicated | Parquet | Snappy compressed, partitioned by source category |
| Final corpus | Parquet | Versioned, checksummed, write-protected |

### JSONL Record Schema

```json
{
  "id": "unique record hash",
  "source_name": "NVD",
  "source_url": "https://nvd.nist.gov/...",
  "access_date": "YYYY-MM-DD",
  "content_type": "vulnerability_advisory",
  "license": "public_domain",
  "license_status": "green",
  "domain_category": "vulnerabilities",
  "raw_text": "...",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
}
```

---

## Source Registry

All approved sources are tracked in `sources/source_registry.csv`.

Columns: `source_name, url, category, format, size_estimate, access_method, license, license_status, quality_score, domain_score, extraction_difficulty, scalability_score, overall_rank, notes`

License status values:
- **Green** — open license, training use explicitly permitted
- **Yellow** — ambiguous license, conditional use with review
- **Red** — rejected, proprietary or training use not permitted

---

## Weekly Progress

| Week | Status | Summary |
|------|--------|---------|
| 1 | In Progress | Source discovery, licensing, pipeline planning |
| 2 | Pending | Extraction, deduplication, unified storage |
| 3 | Pending | Quality filtering, cleaning, statistics |
| 4 | Pending | Freeze, data card, handoff |

---

## How to Contribute

1. Clone the repo
2. Create a branch named `week[N]-[your-name]` for your work
3. Never commit directly to `main`
4. Open a pull request and get one teammate to review before merging
5. Log all significant actions in the `logs/` folder

---

## Status
**Current Week:** Week 1  
**Last Updated:** June 2026  
**Dataset Version:** v0.1-alpha (in progress)
