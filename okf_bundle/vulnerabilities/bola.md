---
type: vulnerability
title: "Broken Object Level Authorization (BOLA)"
description: "An API acts on an object the caller does not own because ownership is never checked."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api1", "authorization", "idor"]
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
# Broken Object Level Authorization (BOLA)

BOLA (a.k.a. IDOR) occurs when an endpoint accepts an object identifier — user ID, account
number, order ID — and acts on it without confirming the authenticated caller may access
*that* object.[^ch3] It is among the most common and damaging API weaknesses.

## How it shows up
* `GET /api/accounts/5502` returns another customer's record while signed in as 5501.
* IDs may be sequential numbers, emails, names, or nested `group/user` pairs. Predictable
  IDs make discovery easy, but the real defect is the missing ownership check.[^ch10]
* A different status code or response time for "exists but not yours" vs "does not exist"
  still leaks which objects exist.[^ch10]

## Verify it is absent
Using two legitimate test accounts, confirm that each account can only read and modify its
own objects (see [Authorization Assurance](/runbooks/api_testing/authorization_testing.md)).

## Prevent
Apply the [Object-Level Authorization Control](/controls/object_level_authorization.md): derive ownership from the token, check it on every read and write,
and return the same `404` whether an object is missing or simply not the caller's.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch10]: Hacking APIs, Ch. 10 Exploiting Authorization, PDF pp. 251-264.
