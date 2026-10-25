---
okf_version: "0.2"
---
# Enterprise Operations & Security Knowledge Bundle

Curated OKF v0.2 bundle. Consuming agents should start here (progressive disclosure)
before traversing individual concepts.

## Policies
* [Remote Access Policy](/policies/remote_access.md) - Zero-trust authentication and tunnel rules for remote engineers.
* [Data Governance Policy](/policies/data_governance.md) - PII classification, masking and retention.

## Runbooks
* [Zero Trust VPN Runbook](/runbooks/zero_trust_vpn.md) - Diagnosing mTLS certificate and tunnel drops.

## Computations
* [Gateway SLA Uptime Check](/computations/sla_uptime_check.md) - Attested 30-day availability calculation per region.

## API Security (defensive knowledge base)
Built from *Hacking APIs* (Corey J. Ball) and the OWASP API Security Top 10, for the
API-security assistant and secure-request demo.
* [API Security Knowledge Hub](/api_security/overview.md) - Start here: weakness classes, assurance checklists, controls.
* [API Security Policy](/policies/api_security_policy.md) - Mandatory controls every production API must implement.
* [OWASP API Top 10 (2023)](/standards/owasp_api_top10_2023.md) - Current taxonomy and bundle mapping.
* `vulnerabilities/` - 13 weakness classes (BOLA, BFLA, broken auth, JWT, injection, mass assignment, …).
* `controls/` - 8 defensive controls that prevent them.
* `runbooks/api_testing/` - 10 assurance checklists for authorized reviews.
