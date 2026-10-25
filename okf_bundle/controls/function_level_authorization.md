---
type: control
title: "Function-Level Authorization Control"
description: "Deny by default and map every route and method to an explicit allowed role."
status: stable
stale_after: "2027-10-25"
tags: ["authorization", "control", "rbac"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch10
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 10 Exploiting Authorization (PDF pp. 251-264)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
verified:
  - by: "human:appsec_lead"
    at: "2026-10-25"
---
# Function-Level Authorization Control

Prevents [BFLA](/vulnerabilities/bfla.md). Each route+method pair is mapped to the roles permitted to call it,
and the default for an unmapped or unauthenticated caller is deny.[^ch3]

## Implementation
* Centralise role checks in middleware, not scattered per handler.
* Treat HTTP methods distinctly: allowing `GET` on a resource does not allow `PUT`/`DELETE`.
* Do not rely on hiding admin routes from the UI; enforce roles on the server.[^ch10]
* Keep admin and user functionality behind the same enforcement layer.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch10]: Hacking APIs, Ch. 10 Exploiting Authorization, PDF pp. 251-264.
