---
type: policy
title: "API Security Policy"
description: "Mandatory controls every production API must implement before release."
status: stable
stale_after: "2027-10-25"
tags: ["api-security", "policy"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: appA
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Appendix A API Hacking Checklist (PDF pp. 349-350)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
verified:
  - by: "human:appsec_lead"
    at: "2026-10-25"
---
# API Security Policy

Every API exposed beyond its own service boundary must satisfy the controls below before
release, and must be re-reviewed with the [API Assurance Checklist](/runbooks/api_testing/api_hacking_checklist.md) at each major version.[^appA]

## Mandatory requirements
1. **Authorization on every object and function** — enforce the [Object-Level Authorization Control](/controls/object_level_authorization.md) and the
   [Function-Level Authorization Control](/controls/function_level_authorization.md). Never rely on unguessable IDs or hidden admin routes for protection.[^ch3]
2. **Authentication** — tokens follow the [Token Hardening Control](/controls/token_hardening.md); never place API keys or tokens in
   URLs or client-side code.
3. **Input** — request bodies are validated against an allowlist schema per the [Input Validation Control](/controls/input_validation.md).
4. **Output** — responses are shaped server-side per the [Response Filtering Control](/controls/response_filtering.md); customer PII is
   additionally governed by the [Data Governance Policy](/policies/data_governance.md).
5. **Abuse resistance** — the [Rate Limiting Control](/controls/rate_limiting.md) applies to all authentication and costly endpoints.
6. **Hygiene** — the [Secure Configuration Control](/controls/secure_configuration.md) and [API Inventory Control](/controls/api_inventory.md) apply to every deployed version.

Related knowledge: [API Security Knowledge Hub](/api_security/overview.md).

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^appA]: Hacking APIs, Appendix A API Hacking Checklist, PDF pp. 349-350.
