---
type: runbook
title: "Endpoint Review"
description: "Map each endpoint's parameters, auth and responses; spot disclosure, exposure and logic gaps."
status: stable
stale_after: "2027-10-25"
tags: ["analysis", "documentation"]
sources:
  - id: ch7
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 7 Endpoint Analysis (PDF pp. 183-206)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Endpoint Review

1. **Read the documentation** — base paths, auth scheme, parameters, admin sections.[^ch7]
2. **Build a request collection** — import OpenAPI specs, or record normal traffic through a
   proxy.[^ch7]
3. **Use the API as intended** to learn baseline behaviour.
4. **Exercise documented privileged actions** (seeds the [Authorization Assurance](/runbooks/api_testing/authorization_testing.md)).
5. **Analyse responses** for [Information Disclosure](/vulnerabilities/information_disclosure.md), [Excessive Data Exposure](/vulnerabilities/excessive_data_exposure.md), [Security Misconfiguration](/vulnerabilities/security_misconfiguration.md) (headers, TLS, verbose
   errors) and [Business Logic Flaws](/vulnerabilities/business_logic_flaws.md).[^ch7]

[^ch7]: Hacking APIs, Ch. 7 Endpoint Analysis, PDF pp. 183-206.
