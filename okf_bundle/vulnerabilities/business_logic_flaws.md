---
type: vulnerability
title: "Business Logic Flaws"
description: "Intended features abused because the provider assumed clients would behave as instructed."
status: stable
stale_after: "2027-10-25"
tags: ["business-logic", "trust"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch15
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 15 Data Breaches and Bug Bounties (PDF pp. 335-346)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Business Logic Flaws

Features that work as designed but can be misused because the provider *trusted* consumers
to follow instructions.[^ch3] Documentation phrases like "only use X for Y" or "only admins
should call Z" often signal missing technical enforcement.

## Examples
* Client-side controls: a login request carrying `MFA=true` that can be flipped to `false`
  because enforcement lives only in the browser.[^ch3]
* Partners with legitimate access reusing data beyond their contract — a trust failure seen
  in real breaches.[^ch15]
* Coupons, refunds or transfers that can be replayed or run with negative values.

## Prevent
Enforce every business rule server-side, model misuse cases during design, and monitor
sensitive flows. Scanners rarely catch these; manual review via the [Endpoint Review](/runbooks/api_testing/endpoint_analysis.md) is
needed. Maps to API6 in the [OWASP API Top 10 (2023)](/standards/owasp_api_top10_2023.md).

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch15]: Hacking APIs, Ch. 15 Data Breaches and Bug Bounties, PDF pp. 335-346.
