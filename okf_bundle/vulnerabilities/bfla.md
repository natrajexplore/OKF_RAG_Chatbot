---
type: vulnerability
title: "Broken Function Level Authorization (BFLA)"
description: "A low-privilege caller can invoke actions reserved for another role, such as admin functions."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api5", "authorization"]
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
---
# Broken Function Level Authorization (BFLA)

BFLA is the action-level counterpart of [BOLA](/vulnerabilities/bola.md): instead of reading someone else's
object, a user performs a *function* reserved for another role — creating users, deleting
accounts, resetting passwords.[^ch3]

## Patterns
* Admin routes such as `/admin/users` that only hide links in the UI but accept any token.
* Privilege expressed through HTTP methods: `GET` allowed, but `PUT`/`DELETE` on the same
  resource is never role-checked.
* Published admin documentation that reveals exactly which privileged calls exist.[^ch3]

## Verify it is absent
Confirm that a non-admin token cannot perform documented admin actions, and that admin
actions re-check the role on the server (see [Authorization Assurance](/runbooks/api_testing/authorization_testing.md)).[^ch10]

## Prevent
Apply the [Function-Level Authorization Control](/controls/function_level_authorization.md): deny by default and map every route + method to an explicit role.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch10]: Hacking APIs, Ch. 10 Exploiting Authorization, PDF pp. 251-264.
