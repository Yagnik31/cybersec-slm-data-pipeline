#!/usr/bin/env python3
"""Catalog of sources for the corpus. One row = one dataset / scrape target.

DATASETS go through fetch.py; PDFS + FEEDS go through scrape.py; SITES go
through scrape_html.py. Output lands under <project>/raw_data/<domain>/...
Domain = top-level folder; subdomain = the topic within it.
"""

from .common import GOV_US, GOV_IN, MITRE

# kind: hf | kaggle | github | url
# each: (kind, ref, domain, description, license, [url for github/url])
DATASETS = [
    # ---------------- Malware Analysis ----------------
    ("kaggle", "joebeachcapital/windows-malwares", "Malware Analysis",
     "Windows PE malware features", "to-verify"),
    # NOTE: mjbommar/binary-30k excluded — 42 shards expand to ~95 GB of JSONL,
    # far past the 5 GB cap. Kept as a placeholder folder only.
    ("kaggle", "shashwatwork/android-malware-dataset-for-machine-learning",
     "Malware Analysis", "Android malware features (Drebin)", "to-verify"),
    ("kaggle", "ang3loliveira/malware-analysis-datasets-top1000-pe-imports",
     "Malware Analysis", "Top-1000 PE import features", "to-verify"),
    ("kaggle", "dannyrevaldo/android-malware-detection-dataset",
     "Malware Analysis", "Android malware detection", "to-verify"),
    ("kaggle", "subhajournal/android-ransomware-detection",
     "Malware Analysis", "Android ransomware flows", "to-verify"),
    ("kaggle", "saurabhshahane/classification-of-malwares",
     "Malware Analysis", "CLaMP PE malware classification", "to-verify"),
    ("kaggle", "saurabhshahane/android-malware-dataset",
     "Malware Analysis", "Android malware (static)", "to-verify"),
    ("url", "dike-malware", "Malware Analysis", "DikeDataset malicious PE labels",
     "MIT", "https://raw.githubusercontent.com/iosifache/DikeDataset/main/labels/malware.csv"),
    ("url", "dike-benign", "Malware Analysis", "DikeDataset benign PE labels",
     "MIT", "https://raw.githubusercontent.com/iosifache/DikeDataset/main/labels/benign.csv"),
    # ---------------- Network ----------------
    ("kaggle", "mrwellsdavid/unsw-nb15", "Network Security", "UNSW-NB15 IDS benchmark", "to-verify"),
    ("kaggle", "dhoogla/unswnb15", "Network Security", "UNSW-NB15 cleaned", "to-verify"),
    ("kaggle", "galaxyh/kdd-cup-1999-data", "Network Security", "KDD Cup 1999 IDS", "to-verify"),
    ("kaggle", "aikenkazin/ml-edge-iiot-dataset", "Network Security",
     "Edge-IIoTset IoT/IIoT IDS", "to-verify"),
    ("kaggle", "dhoogla/cicids2017", "Network Security", "CICIDS2017 cleaned", "to-verify"),
    ("kaggle", "dhoogla/cicddos2019", "Network Security", "CIC-DDoS2019 cleaned", "to-verify"),
    # ---------------- Application ----------------
    ("kaggle", "cyberprince/web-application-payloads-dataset", "Application Security",
     "Web attack payloads", "to-verify"),
    ("hf", "AlicanKiraz0/Cybersecurity-Dataset-v1", "Application Security",
     "Web-sec Q&A (XSS/SQLi/CSRF)", "to-verify"),
    ("kaggle", "ispangler/csic-2010-web-application-attacks", "Application Security",
     "HTTP CSIC 2010 web attacks", "to-verify"),
    ("kaggle", "syedsaqlainhussain/cross-site-scripting-xss-dataset-for-deep-learning",
     "Application Security", "XSS payloads", "to-verify"),
    ("url", "uci-phishing-websites", "Application Security", "UCI phishing websites (30 feat)",
     "CC BY 4.0", "https://archive.ics.uci.edu/static/public/327/phishing+websites.zip"),
    # ---------------- Cloud ----------------
    ("kaggle", "nobukim/aws-cloudtrails-dataset-from-flaws-cloud", "Cloud Security",
     "AWS CloudTrail attack logs", "to-verify"),
    ("kaggle", "alaakhaledd/cloud-security-dataset", "Cloud Security",
     "Cloud security telemetry", "to-verify"),
    # ---------------- IAM ----------------
    ("kaggle", "dasgroup/rba-dataset", "Identity Access and Management", "Risk-based auth logins (3.3M)", "to-verify"),
    ("kaggle", "lako65/ssh-brute-force-ipuserpassword", "Identity Access and Management",
     "SSH brute-force attempts", "to-verify"),
    ("kaggle", "rasikaekanayakadevlk/user-activity-dataset", "Identity Access and Management",
     "Behavioral auth signals", "to-verify"),
    # ---------------- Penetration Testing & Vulnerability Management ----------------
    ("kaggle", "sid321axn/malicious-urls-dataset",
     "Penetration Testing and Vulnerability Management", "651k malicious URLs", "to-verify"),
    # ---------------- Threat Intelligence ----------------
    ("hf", "zefang-liu/phishing-email-dataset", "Threat Intelligence",
     "Phishing vs benign emails", "to-verify"),
    ("hf", "darkknight25/phishing_benign_email_dataset", "Threat Intelligence",
     "Phishing/benign email", "to-verify"),
    ("kaggle", "shashwatwork/web-page-phishing-detection-dataset",
     "Threat Intelligence", "Web-page phishing features", "to-verify"),
    ("url", "phiusiil-phishing-url", "Threat Intelligence",
     "UCI PhiUSIIL phishing URLs (235k)", "CC BY 4.0",
     "https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip"),
    # ---------------- Incident Response & Forensics ----------------
    ("hf", "darkknight25/Incident_Response_Playbook_Dataset",
     "Incident Response and Forensics", "IR playbooks", "to-verify"),
    ("kaggle", "Microsoft/microsoft-security-incident-prediction",
     "Incident Response and Forensics", "GUIDE SOC incident triage", "cc-by-4.0"),
    # ---------------- Security Operations ----------------
    ("kaggle", "dnkumars/cybersecurity-intrusion-detection-dataset",
     "Security Operations", "Login/session intrusion", "to-verify"),
    ("kaggle", "rasikaekanayakadevlk/security-monitoring-and-user-management-dataset",
     "Security Operations", "Security monitoring logs", "to-verify"),
    # ---------------- Data Security & Privacy ----------------
    ("hf", "ai4privacy/pii-masking-200k", "Data Security and Privacy",
     "PII detection / masking (200k)", "to-verify"),
    ("hf", "ai4privacy/pii-masking-300k", "Data Security and Privacy",
     "PII detection / masking (300k)", "to-verify"),
    ("hf", "ealvaradob/phishing-dataset", "Threat Intelligence",
     "Phishing URLs / emails / HTML", "to-verify"),
    ("kaggle", "nsaravana/malware-detection", "Malware Analysis",
     "Malware detection features", "to-verify"),
]

# (domain, slug, title, license, url)
PDFS = [
    ("Incident Response and Forensics", "nist-sp800-61",
     "NIST SP 800-61r2 Incident Handling Guide", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf"),
    ("Incident Response and Forensics", "nist-sp800-86",
     "NIST SP 800-86 Forensic Techniques", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf"),
    ("Data Security and Privacy", "nist-sp800-122",
     "NIST SP 800-122 Protecting PII", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-122.pdf"),
    ("Data Security and Privacy", "india-dpdp-act-2023",
     "India Digital Personal Data Protection Act 2023", GOV_IN,
     "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf"),
    ("Governance, Risk and Compliance", "nist-sp800-53r5",
     "NIST SP 800-53r5 Security & Privacy Controls", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf"),
    ("Governance, Risk and Compliance", "nist-sp800-37r2",
     "NIST SP 800-37r2 Risk Management Framework", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-37r2.pdf"),
    ("Governance, Risk and Compliance", "india-it-act-2000",
     "India Information Technology Act 2000", GOV_IN,
     "https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf"),
    ("Penetration Testing and Vulnerability Management", "nist-sp800-115",
     "NIST SP 800-115 Security Testing", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf"),
    ("Cryptography", "nist-sp800-57", "NIST SP 800-57 Key Management", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf"),
    ("Cryptography", "nist-fips-203-mlkem", "NIST FIPS 203 ML-KEM (PQC)", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf"),
    ("Cryptography", "nist-fips-204-mldsa", "NIST FIPS 204 ML-DSA (PQC)", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf"),
    ("Cryptography", "nist-fips-205-slhdsa", "NIST FIPS 205 SLH-DSA (PQC)", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf"),
    ("Cryptography", "nist-sp800-208", "NIST SP 800-208 Hash-Based Signatures", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-208.pdf"),
    ("Identity Access and Management", "nist-sp800-63b", "NIST SP 800-63B Digital Identity", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b.pdf"),
    ("Governance, Risk and Compliance", "nist-sp800-30r1",
     "NIST SP 800-30r1 Guide for Conducting Risk Assessments", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf"),
    ("Security Operations", "nist-sp800-92", "NIST SP 800-92 Log Management", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-92.pdf"),
    ("Network Security", "nist-sp800-94", "NIST SP 800-94 IDS/IPS", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-94.pdf"),
    ("Threat Intelligence", "nist-sp800-150",
     "NIST SP 800-150 Cyber Threat Information Sharing", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-150.pdf"),
    ("Incident Response and Forensics", "nist-sp800-184",
     "NIST SP 800-184 Cybersecurity Event Recovery", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-184.pdf"),
    ("Penetration Testing and Vulnerability Management", "nist-sp800-40r4",
     "NIST SP 800-40r4 Enterprise Patch Management", GOV_US,
     "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-40r4.pdf"),
]

# (domain, slug, start_url, license, use_js, max_pages, allow_prefix, description)
# Only robots.txt-permitted sites (verified). NIST/CISA/OWASP/Wikipedia block
# bots but publish downloadable data — fetch those as feeds instead of crawling.
SITES = [
    ("Threat Intelligence", "mitre-attack-web",
     "https://attack.mitre.org/techniques/enterprise/",
     "MITRE ATT&CK Terms (free w/ attribution)", False, 70,
     "https://attack.mitre.org/techniques/", "MITRE ATT&CK technique pages"),
    ("Penetration Testing and Vulnerability Management", "capec-web",
     "https://capec.mitre.org/data/definitions/1000.html",
     "MITRE CAPEC Terms (free w/ attribution)", False, 70,
     "https://capec.mitre.org/data/definitions/", "MITRE CAPEC attack patterns"),
]

# (domain, slug, title, license, url, json_key) -> records = data[json_key]
FEEDS = [
    ("Threat Intelligence", "cisa-kev", "CISA Known Exploited Vulnerabilities",
     "Public Domain (CISA)",
     "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
     "vulnerabilities"),
    ("Threat Intelligence", "mitre-attack", "MITRE ATT&CK Enterprise", MITRE,
     "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json",
     "objects"),
    ("Threat Intelligence", "mitre-attack-mobile", "MITRE ATT&CK Mobile", MITRE,
     "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/mobile-attack/mobile-attack.json",
     "objects"),
    ("Threat Intelligence", "mitre-attack-ics", "MITRE ATT&CK ICS", MITRE,
     "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/ics-attack/ics-attack.json",
     "objects"),
]
