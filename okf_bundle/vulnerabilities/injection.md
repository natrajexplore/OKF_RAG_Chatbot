---
type: vulnerability
title: "Injection"
description: "Unsanitised input reaches an interpreter: SQL, NoSQL, OS command, or script injection via API parameters."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api8", "injection", "sqli"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch12
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 12 Injection (PDF pp. 277-292)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Injection

Injection occurs when request data is passed to a backend interpreter — a SQL or NoSQL
database, an OS shell, a template engine, a browser — without being kept separate from
code.[^ch3]

## Signals
Verbose database errors, `500` responses, or changed result counts/timing when input
contains metacharacters such as `'`, `"`, `;`, `--`, `$ne` or `|`.[^ch12]

## Variants covered in the book
* SQL and NoSQL injection.
* OS command injection through parameters passed to shell utilities.[^ch12]
* Cross-site/cross-API scripting where API data is later rendered by another app.
* Path traversal through file parameters.

## Verify & prevent
Review with the [Injection Resistance Assurance](/runbooks/api_testing/injection_testing.md). Prevent with the [Input Validation Control](/controls/input_validation.md): parameterised queries, no shell
string building, and output encoding.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch12]: Hacking APIs, Ch. 12 Injection, PDF pp. 277-292.
