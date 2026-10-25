---
type: vulnerability
title: "GraphQL Risks"
description: "GraphQL-specific risks: introspection leakage, exposed IDEs, per-field authorization gaps, batching abuse."
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
# GraphQL Risks

GraphQL exposes a single endpoint (usually `/graphql`) and lets clients compose queries, so
classic per-route controls do not map neatly onto it.[^ch14]

## Risks
* **Introspection enabled** in production reveals the whole schema — every query, mutation
  and field, including admin ones.[^ch14]
* **GraphiQL/Playground IDE** reachable, sometimes behind a cookie or flag a client can
  toggle.[^ch14]
* **Per-field authorization gaps** — the same [BOLA](/vulnerabilities/bola.md) and [BFLA](/vulnerabilities/bfla.md) issues, now inside
  resolvers.
* **Deep, nested or batched queries** that slip past [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md) counted per HTTP request.
* [Injection](/vulnerabilities/injection.md) through resolver arguments passed to databases or the OS.

## Verify & prevent
Review with the [GraphQL Hardening Review](/runbooks/api_testing/graphql_testing.md). Disable introspection and IDEs in production, authorize in
every resolver, and cap query depth, complexity and batch size.

[^ch14]: Hacking APIs, Ch. 14 Attacking GraphQL, PDF pp. 313-334.
