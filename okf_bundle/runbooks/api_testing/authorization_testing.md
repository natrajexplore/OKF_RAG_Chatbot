---
type: runbook
title: "Authorization Assurance"
description: "Use multiple accounts to confirm object- and function-level access is enforced server-side."
status: stable
stale_after: "2027-10-25"
tags: ["authorization", "bola", "bfla"]
sources:
  - id: ch10
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 10 Exploiting Authorization (PDF pp. 251-264)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Authorization Assurance

Use at least two legitimate test accounts (and roles where available).[^ch10]

## Object level ([BOLA](/vulnerabilities/bola.md))
* Create resources as account A; attempt to read and modify them with account B's token.
* Confirm identical `404` responses for missing vs not-owned objects.

## Function level ([BFLA](/vulnerabilities/bfla.md))
* Attempt documented admin actions with a non-admin token and confirm they are denied.
* Confirm each HTTP method on a resource is role-checked independently.

Remediate with the [Object-Level Authorization Control](/controls/object_level_authorization.md) and the [Function-Level Authorization Control](/controls/function_level_authorization.md).

[^ch10]: Hacking APIs, Ch. 10 Exploiting Authorization, PDF pp. 251-264.
