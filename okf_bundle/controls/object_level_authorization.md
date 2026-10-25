---
type: control
title: "Object-Level Authorization Control"
description: "Check that the authenticated caller owns or may access each object, on every request."
status: stable
stale_after: "2027-10-25"
tags: ["authorization", "control"]
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
# Object-Level Authorization Control

Prevents [BOLA](/vulnerabilities/bola.md). For every request that names an object (ID in the path, query or
body), the server derives the caller's identity from the verified token and confirms that
identity may access *that specific object* before reading or writing it.[^ch3]

## Implementation
* Scope every data query by owner, e.g. `WHERE id = :id AND owner_id = :caller`.[^ch10]
* Return an identical `404 Not Found` for "does not exist" and "exists but not yours" so
  the response does not reveal which objects exist.
* Do not trust IDs just because they look random; authorization is required regardless.
* Add automated tests that request one account's objects with another account's token.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch10]: Hacking APIs, Ch. 10 Exploiting Authorization, PDF pp. 251-264.
