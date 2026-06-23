# Master Source List

Tracks every candidate source. Update `Status` as sources move through evaluation.
When a source reaches **In Pipeline**, add it to `manifest.py` and record the manifest entry here.

**Statuses:** `Candidate` → `Evaluating` → `Approved` → `In Pipeline` → `Rejected`

---

## Threat Intelligence

| Name | URL | Format | Access | Size | License | Status | Manifest Entry | Notes |
|---|---|---|---|---|---|---|---|---|
| MITRE ATT&CK Enterprise | https://attack.mitre.org/ | JSON (STIX) | Free | 700+ techniques | Apache-2.0 / ATT&CK Terms | In Pipeline | `FEEDS["mitre-attack"]` | Also mobile + ICS variants added |
| MITRE ATT&CK Mobile | https://attack.mitre.org/matrices/mobile/ | JSON (STIX) | Free | ~100 techniques | Apache-2.0 / ATT&CK Terms | In Pipeline | `FEEDS["mitre-attack-mobile"]` | |
| MITRE ATT&CK ICS | https://attack.mitre.org/matrices/ics/ | JSON (STIX) | Free | ~80 techniques | Apache-2.0 / ATT&CK Terms | In Pipeline | `FEEDS["mitre-attack-ics"]` | |
| CISA Known Exploited Vulnerabilities | https://www.cisa.gov/known-exploited-vulnerabilities-catalog | JSON | Free | ~1,000 CVEs | Public Domain | In Pipeline | `FEEDS["cisa-kev"]` | |
| AlienVault OTX | https://otx.alienvault.com/api | JSON | Free API key | Millions of pulses | OTX Terms | Candidate | — | Rich text threat reports; needs API key |
| Abuse.ch (MalwareBazaar, Feodo, URLhaus) | https://abuse.ch/ | JSON/CSV | Free | Millions of records | CC0 | Candidate | — | IOC-heavy, text descriptions limited |

---

## Vulnerability Databases

| Name | URL | Format | Access | Size | License | Status | Manifest Entry | Notes |
|---|---|---|---|---|---|---|---|---|
| NVD CVE Database | https://nvd.nist.gov/developers/vulnerabilities | JSON | Free API key | 250,000+ CVEs | Public Domain | Candidate | — | Gold standard; descriptions are best CVE text |
| CIRCL CVE Search | https://cve.circl.lu/api/ | JSON | Free | Full CVE mirror | Public Domain | Candidate | — | Good backup to NVD with extra metadata |
| MITRE CWE | https://cwe.mitre.org/data/ | XML/JSON | Free | 900+ weaknesses | Public Domain | Candidate | — | Weakness descriptions complement CVE data |

---

## Documents & Standards

| Name | URL | Format | Access | Size | License | Status | Manifest Entry | Notes |
|---|---|---|---|---|---|---|---|---|
| NIST SP 800-61r2 (Incident Handling) | https://nvlpubs.nist.gov/... | PDF | Free | ~90 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-61"]` | |
| NIST SP 800-86 (Forensics) | https://nvlpubs.nist.gov/... | PDF | Free | ~121 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-86"]` | |
| NIST SP 800-53r5 (Security Controls) | https://nvlpubs.nist.gov/... | PDF | Free | ~492 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-53r5"]` | |
| NIST SP 800-37r2 (RMF) | https://nvlpubs.nist.gov/... | PDF | Free | ~183 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-37r2"]` | |
| NIST SP 800-115 (Security Testing) | https://nvlpubs.nist.gov/... | PDF | Free | ~80 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-115"]` | |
| NIST SP 800-57 (Key Management) | https://nvlpubs.nist.gov/... | PDF | Free | ~156 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-57"]` | |
| NIST SP 800-63B (Digital Identity) | https://nvlpubs.nist.gov/... | PDF | Free | ~79 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-63b"]` | |
| NIST SP 800-92 (Log Management) | https://nvlpubs.nist.gov/... | PDF | Free | ~72 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-92"]` | |
| NIST SP 800-94 (IDS/IPS) | https://nvlpubs.nist.gov/... | PDF | Free | ~54 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-94"]` | |
| NIST SP 800-150 (Threat Sharing) | https://nvlpubs.nist.gov/... | PDF | Free | ~38 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-150"]` | |
| NIST SP 800-184 (Recovery) | https://nvlpubs.nist.gov/... | PDF | Free | ~52 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-184"]` | |
| NIST SP 800-122 (PII) | https://nvlpubs.nist.gov/... | PDF | Free | ~53 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-122"]` | |
| NIST SP 800-30r1 (Risk Assessments) | https://nvlpubs.nist.gov/... | PDF | Free | ~95 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-30r1"]` | |
| NIST SP 800-40r4 (Patch Management) | https://nvlpubs.nist.gov/... | PDF | Free | ~35 pages | Public Domain | In Pipeline | `PDFS["nist-sp800-40r4"]` | |
| NIST FIPS 203/204/205 (PQC) | https://nvlpubs.nist.gov/... | PDF | Free | ~60 pages each | Public Domain | In Pipeline | `PDFS["nist-fips-*"]` | Post-quantum crypto standards |
| India DPDP Act 2023 | https://www.meity.gov.in/... | PDF | Free | ~30 pages | GOV_IN | In Pipeline | `PDFS["india-dpdp-act-2023"]` | |
| India IT Act 2000 | https://www.indiacode.nic.in/... | PDF | Free | ~50 pages | GOV_IN | In Pipeline | `PDFS["india-it-act-2000"]` | |
| USENIX Security Proceedings | https://www.usenix.org/publications/proceedings | PDF | Free | 1,000+ papers | Open Access | Candidate | — | Top-tier research; needs per-paper scraping |

---

## Research Corpora

| Name | URL | Format | Access | Size | License | Status | Manifest Entry | Notes |
|---|---|---|---|---|---|---|---|---|
| ArXiv cs.CR | https://arxiv.org/list/cs.CR/recent | PDF/XML | Free (OAI-PMH or arxiv lib) | 20,000+ papers | arXiv non-exclusive | Candidate | — | High quality technical text; bulk export available |
| Semantic Scholar | https://api.semanticscholar.org/ | JSON | Free API key | Millions of papers | S2 Terms | Candidate | — | Abstracts + open-access full text |

---

## Community / Web

| Name | URL | Format | Access | Size | License | Status | Manifest Entry | Notes |
|---|---|---|---|---|---|---|---|---|
| MITRE ATT&CK Website | https://attack.mitre.org/techniques/enterprise/ | HTML | Free (robots.txt OK) | ~70 pages | ATT&CK Terms | In Pipeline | `SITES["mitre-attack-web"]` | Crawled for technique detail pages |
| MITRE CAPEC | https://capec.mitre.org/ | HTML | Free (robots.txt OK) | ~70 pages | ATT&CK Terms | In Pipeline | `SITES["capec-web"]` | Attack pattern pages |
| Security Stack Exchange | https://security.stackexchange.com/ | XML dump | Free (archive.org) | 100,000+ threads | CC BY-SA 4.0 | Candidate | — | Q&A format great for SLM; data dump easier than crawl |
| GitHub Security Repos | https://github.com/topics/cybersecurity | Markdown/Text | Free (GH API key) | Thousands of repos | Mixed | Candidate | — | READMEs, writeups; needs repo-level filtering |

---

## Open Datasets (HuggingFace)

| Name | HF Ref | Domain | License | Status | Manifest Entry | Notes |
|---|---|---|---|---|---|---|
| Cybersecurity Dataset v1 | AlicanKiraz0/Cybersecurity-Dataset-v1 | Application Security | to-verify | In Pipeline | `DATASETS[hf]` | Web-sec Q&A |
| Phishing Email Dataset | zefang-liu/phishing-email-dataset | Threat Intelligence | to-verify | In Pipeline | `DATASETS[hf]` | |
| Phishing/Benign Email | darkknight25/phishing_benign_email_dataset | Threat Intelligence | to-verify | In Pipeline | `DATASETS[hf]` | |
| IR Playbook Dataset | darkknight25/Incident_Response_Playbook_Dataset | Incident Response | to-verify | In Pipeline | `DATASETS[hf]` | |
| PII Masking 200k | ai4privacy/pii-masking-200k | Data Security | to-verify | In Pipeline | `DATASETS[hf]` | Uses `source_text` column — now mapped via `enrich_df` |
| PII Masking 300k | ai4privacy/pii-masking-300k | Data Security | to-verify | In Pipeline | `DATASETS[hf]` | |
| Phishing Dataset (multi) | ealvaradob/phishing-dataset | Threat Intelligence | to-verify | In Pipeline | `DATASETS[hf]` | URLs + emails + HTML |

---

## Open Datasets (Kaggle) — Feature/Tabular

> ⚠️ These are tabular feature datasets. They produce no `text` field and will be dropped by the cleaning pipeline. Consider removing from `manifest.py` or adding a serialization layer before they add value to SLM training.

| Name | Kaggle Ref | Domain | Status | Notes |
|---|---|---|---|---|
| Windows Malware PE Features | joebeachcapital/windows-malwares | Malware Analysis | Review | No text — PE feature matrix |
| Android Malware (Drebin) | shashwatwork/android-malware-dataset-for-machine-learning | Malware Analysis | Review | No text |
| Top-1000 PE Imports | ang3loliveira/malware-analysis-datasets-top1000-pe-imports | Malware Analysis | Review | No text |
| UNSW-NB15 | mrwellsdavid/unsw-nb15 | Network Security | Review | No text — network flow features |
| KDD Cup 1999 | galaxyh/kdd-cup-1999-data | Network Security | Review | No text — oldest IDS benchmark |
| CICIDS2017 | dhoogla/cicids2017 | Network Security | Review | No text |
| Microsoft GUIDE (SOC Triage) | Microsoft/microsoft-security-incident-prediction | Incident Response | Approved | Has text fields — keep |
| Web Attack Payloads | cyberprince/web-application-payloads-dataset | Application Security | Approved | Payload strings — usable text |
| XSS Payloads | syedsaqlainhussain/cross-site-scripting-xss-dataset-for-deep-learning | Application Security | Approved | Payload strings — usable text |
| SSH Brute Force | lako65/ssh-brute-force-ipuserpassword | IAM | Review | No text |
| Malicious URLs (651k) | sid321axn/malicious-urls-dataset | PenTest/VulnMgmt | Approved | URL strings — usable text |

---

## APIs Requiring Keys (Future Work)

| Name | API Docs | Key Required | Cost | Notes |
|---|---|---|---|---|
| VirusTotal | https://developers.virustotal.com/ | Yes (free tier) | Free / Paid | Malware analysis reports |
| Shodan | https://developer.shodan.io/ | Yes (free tier) | Free / Paid | Internet exposure context |
| NVD | https://nvd.nist.gov/developers | Yes (free) | Free | Priority addition — add to manifest.py next |
