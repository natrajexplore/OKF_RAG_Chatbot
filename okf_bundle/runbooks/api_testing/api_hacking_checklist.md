---
type: runbook
title: "API Assurance Checklist"
description: "End-to-end ordered checklist for an authorized API security review."
status: stable
stale_after: "2027-10-25"
tags: ["checklist", "methodology"]
sources:
  - id: appA
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Appendix A API Hacking Checklist (PDF pp. 349-350)"
    author: "Corey J. Ball"
  - id: ch6
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 6 Discovery (PDF pp. 151-182)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# API Assurance Checklist

Run only within a written scope and rules of engagement agreed with the API owner.

1. **Scope** — agree targets, environments and test accounts; choose black/grey/white box.
2. **Attack-surface review** — [Attack-Surface Review](/runbooks/api_testing/recon_and_discovery.md).
3. **Endpoint review** — docs, parameters, intended use, response review; [Endpoint Review](/runbooks/api_testing/endpoint_analysis.md).
4. **Authentication assurance** — [Authentication Assurance](/runbooks/api_testing/authentication_testing.md).
5. **Input robustness** — [Input Robustness Assurance](/runbooks/api_testing/fuzzing.md).
6. **Authorization assurance** — [Authorization Assurance](/runbooks/api_testing/authorization_testing.md).
7. **Property-binding assurance** — [Property Binding Assurance](/runbooks/api_testing/mass_assignment_testing.md).
8. **Injection resistance** — [Injection Resistance Assurance](/runbooks/api_testing/injection_testing.md).
9. **Rate-limit assurance** — [Rate-Limit Assurance](/runbooks/api_testing/evasion_and_rate_limit_testing.md).
10. **GraphQL hardening** (if present) — [GraphQL Hardening Review](/runbooks/api_testing/graphql_testing.md).
11. **Report** findings mapped to the [OWASP API Top 10 (2023)](/standards/owasp_api_top10_2023.md) with remediation controls.[^appA]

[^appA]: Hacking APIs, Appendix A API Hacking Checklist, PDF pp. 349-350.
[^ch6]: Hacking APIs, Ch. 6 Discovery, PDF pp. 151-182.
