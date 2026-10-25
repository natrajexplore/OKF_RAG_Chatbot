---
type: runbook
title: "GraphQL Hardening Review"
description: "Confirm introspection, IDEs, resolver authorization and query cost are controlled."
status: stable
stale_after: "2027-10-25"
tags: ["graphql", "introspection"]
sources:
  - id: ch14
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 14 Attacking GraphQL (PDF pp. 313-334)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# GraphQL Hardening Review

For a GraphQL endpoint, confirm:[^ch14]

* **Introspection** is disabled in production.
* **GraphiQL/Playground** is not reachable (including via a toggled cookie/flag).
* **Resolvers authorize** per field — the [BOLA](/vulnerabilities/bola.md)/[BFLA](/vulnerabilities/bfla.md) checks apply inside
  resolvers, not just at the HTTP layer.
* **Query cost** is bounded: depth, complexity and batch size limits defend against
  [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md) evasion.
* **Resolver arguments** are validated to prevent [Injection](/vulnerabilities/injection.md).

Remediate with the [Function-Level Authorization Control](/controls/function_level_authorization.md), [Object-Level Authorization Control](/controls/object_level_authorization.md), [Rate Limiting Control](/controls/rate_limiting.md) and [Input Validation Control](/controls/input_validation.md).

[^ch14]: Hacking APIs, Ch. 14 Attacking GraphQL, PDF pp. 313-334.
