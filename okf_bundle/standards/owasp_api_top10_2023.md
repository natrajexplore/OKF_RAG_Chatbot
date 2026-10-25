---
type: standard
title: "OWASP API Security Top 10 (2023)"
description: "Current OWASP API Top 10 and how it maps to the concepts in this bundle."
status: stable
stale_after: "2027-10-25"
tags: ["owasp", "taxonomy"]
sources:
  - id: owasp-api-2023
    resource: "https://owasp.org/API-Security/editions/2023/en/0x11-t10/"
    title: "OWASP API Security Top 10 - 2023"
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# OWASP API Security Top 10 (2023)

The current OWASP list.[^owasp-api-2023] It folds excessive data exposure and mass
assignment into one property-level category and adds business-flow and SSRF risks. The
book predates it and follows the [OWASP API Top 10 (2019)](/standards/owasp_api_top10_2019.md).[^ch3]

| 2023 ID | Category | Concepts in this bundle |
|---|---|---|
| API1 | Broken Object Level Authorization | [BOLA](/vulnerabilities/bola.md) |
| API2 | Broken Authentication | [Broken Authentication](/vulnerabilities/broken_authentication.md), [JWT Weaknesses](/vulnerabilities/jwt_attacks.md) |
| API3 | Broken Object Property Level Authorization | [Excessive Data Exposure](/vulnerabilities/excessive_data_exposure.md), [Mass Assignment](/vulnerabilities/mass_assignment.md) |
| API4 | Unrestricted Resource Consumption | [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md) |
| API5 | Broken Function Level Authorization | [BFLA](/vulnerabilities/bfla.md) |
| API6 | Unrestricted Access to Sensitive Business Flows | [Business Logic Flaws](/vulnerabilities/business_logic_flaws.md) |
| API7 | Server Side Request Forgery | [Injection](/vulnerabilities/injection.md) (closest related) |
| API8 | Security Misconfiguration | [Security Misconfiguration](/vulnerabilities/security_misconfiguration.md) |
| API9 | Improper Inventory Management | [Improper Assets Management](/vulnerabilities/improper_assets_management.md) |
| API10 | Unsafe Consumption of APIs | [Input Validation Control](/controls/input_validation.md) |

[^owasp-api-2023]: OWASP API Security Top 10 - 2023.
[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
