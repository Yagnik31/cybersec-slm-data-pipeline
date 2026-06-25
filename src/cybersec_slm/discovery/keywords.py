#!/usr/bin/env python3
"""Per-Sub-Domain search keywords and snippet-classification vocabulary.

``DOMAIN_KEYWORDS`` is the curated input to the crawler: each Sub-Domain (the
exact label used in the tracking sheet's ``Sub-Domain`` column) maps to a list
of search phrases. The domain that a phrase belongs to is the *default*
Sub-Domain assigned to whatever the phrase surfaces.

``DOMAIN_VOCAB`` is the fallback signal: when a result is ambiguous, the text of
its title + snippet is scored against each domain's vocabulary and, if some
other domain scores strictly higher than the default, the result is reassigned.

Sub-Domain labels are kept in sync with ``extraction.sources.CATEGORY_TO_DOMAIN``
so discovered rows file under the same folders the rest of the pipeline uses.
"""

from __future__ import annotations

# A qualifier appended to every query to bias results toward usable corpora
# (datasets / repos / docs) rather than marketing pages.
QUERY_QUALIFIER = "dataset OR github OR repository OR corpus"

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "Application Security": [
        "vulnerable source code dataset",
        "secure code review dataset",
        "SAST static analysis labeled dataset",
        "OWASP code vulnerability dataset",
    ],
    "Network Security": [
        "network intrusion detection dataset",
        "network traffic pcap labeled dataset",
        "IDS flow dataset cybersecurity",
        "DDoS attack network dataset",
    ],
    "Cloud Security": [
        "cloud security misconfiguration dataset",
        "kubernetes security dataset",
        "cloud CSPM findings dataset",
        "AWS Azure GCP security best practices dataset",
    ],
    "Identity Access and Management": [
        "identity access management dataset",
        "authentication logs dataset security",
        "privileged access abuse dataset",
        "IAM policy misconfiguration dataset",
    ],
    "Incident Response and Forensics": [
        "digital forensics dataset",
        "incident response playbook dataset",
        "memory forensics dataset",
        "DFIR investigation dataset",
    ],
    "Data Security and Privacy": [
        "PII detection dataset",
        "data loss prevention dataset",
        "data privacy compliance dataset",
        "sensitive data classification dataset",
    ],
    "Penetration Testing and Vulnerability Management": [
        "penetration testing dataset",
        "exploit proof of concept dataset",
        "CVE exploit dataset",
        "vulnerability scan results dataset",
    ],
    "Governance, Risk and Compliance": [
        "security compliance controls dataset",
        "GRC risk register dataset",
        "NIST CSF mapping dataset",
        "ISO 27001 controls dataset",
    ],
    "Cryptography": [
        "cryptography dataset",
        "cipher cryptanalysis dataset",
        "TLS certificate dataset security",
        "encryption algorithms labeled dataset",
    ],
    "Security Operations": [
        "SOC alert triage dataset",
        "SIEM log dataset",
        "security operations detection rules dataset",
        "threat hunting dataset",
    ],
    "Malware Analysis": [
        "malware analysis dataset",
        "malware samples labeled dataset",
        "ransomware behavior dataset",
        "PE binary malware dataset",
    ],
    "Threat Intelligence": [
        "threat intelligence dataset",
        "IOC indicators of compromise dataset",
        "MITRE ATT&CK technique dataset",
        "phishing URL dataset",
    ],
}

# Distinctive terms per domain, used only to break ties on ambiguous results.
DOMAIN_VOCAB: dict[str, set[str]] = {
    "Application Security": {"sast", "owasp", "code", "sql injection", "xss",
                             "vulnerable code", "appsec", "source code"},
    "Network Security": {"intrusion", "ids", "pcap", "netflow", "ddos",
                         "packet", "traffic", "firewall"},
    "Cloud Security": {"cloud", "kubernetes", "aws", "azure", "gcp", "cspm",
                       "container", "s3 bucket", "misconfiguration"},
    "Identity Access and Management": {"iam", "identity", "authentication",
                                       "oauth", "saml", "privileged", "rbac"},
    "Incident Response and Forensics": {"forensics", "incident response",
                                        "dfir", "memory dump", "triage",
                                        "investigation", "artifact"},
    "Data Security and Privacy": {"pii", "privacy", "dlp", "gdpr",
                                  "sensitive data", "anonymization"},
    "Penetration Testing and Vulnerability Management": {
        "penetration", "pentest", "exploit", "proof of concept", "poc",
        "cve", "metasploit", "scan"},
    "Governance, Risk and Compliance": {"compliance", "grc", "nist", "iso 27001",
                                        "controls", "audit", "risk register",
                                        "policy"},
    "Cryptography": {"cryptography", "cipher", "cryptanalysis", "encryption",
                     "tls", "certificate", "hash", "rsa", "aes"},
    "Security Operations": {"soc", "siem", "alert", "detection rule", "sigma",
                            "threat hunting", "triage"},
    "Malware Analysis": {"malware", "ransomware", "trojan", "pe binary",
                         "sandbox", "reverse engineering", "yara"},
    "Threat Intelligence": {"threat intelligence", "ioc", "indicator",
                            "mitre att&ck", "phishing", "apt", "campaign"},
}

# Canonical Sub-Domain labels (the keys above), exposed for CLI validation.
DOMAINS: tuple[str, ...] = tuple(DOMAIN_KEYWORDS)
