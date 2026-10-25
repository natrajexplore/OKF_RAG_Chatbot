---
type: standard
title: "OWASP API Security Top 10 (2019)"
description: "The 2019 OWASP API Top 10 used as the book's taxonomy; superseded by the 2023 edition."
status: deprecated
stale_after: "2027-10-25"
tags: ["owasp", "taxonomy"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# OWASP API Security Top 10 (2019)

**Superseded** — use the [OWASP API Top 10 (2023)](/standards/owasp_api_top10_2023.md) for new work. This edition is retained because the
book's vulnerability chapters are organised around it.[^ch3]

| 2019 ID | Category | Concept |
|---|---|---|
| API1 | Broken Object Level Authorization | [BOLA](/vulnerabilities/bola.md) |
| API2 | Broken User Authentication | [Broken Authentication](/vulnerabilities/broken_authentication.md) |
| API3 | Excessive Data Exposure | [Excessive Data Exposure](/vulnerabilities/excessive_data_exposure.md) |
| API4 | Lack of Resources & Rate Limiting | [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md) |
| API5 | Broken Function Level Authorization | [BFLA](/vulnerabilities/bfla.md) |
| API6 | Mass Assignment | [Mass Assignment](/vulnerabilities/mass_assignment.md) |
| API7 | Security Misconfiguration | [Security Misconfiguration](/vulnerabilities/security_misconfiguration.md) |
| API8 | Injection | [Injection](/vulnerabilities/injection.md) |
| API9 | Improper Assets Management | [Improper Assets Management](/vulnerabilities/improper_assets_management.md) |
| API10 | Insufficient Logging & Monitoring | [Secure Configuration Control](/controls/secure_configuration.md) |

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
