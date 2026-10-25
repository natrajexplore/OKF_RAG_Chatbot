---
type: control
title: "Input Validation Control"
description: "Validate every request against an allowlist schema and separate data from code at every interpreter."
status: stable
stale_after: "2027-10-25"
tags: ["input", "injection", "mass-assignment", "control"]
sources:
  - id: ch11
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 11 Mass Assignment (PDF pp. 265-276)"
    author: "Corey J. Ball"
  - id: ch12
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 12 Injection (PDF pp. 277-292)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
verified:
  - by: "human:appsec_lead"
    at: "2026-10-25"
---
# Input Validation Control

Prevents [Injection](/vulnerabilities/injection.md) and [Mass Assignment](/vulnerabilities/mass_assignment.md) and supports safe consumption of third-party APIs.

## Request shaping
* Bind only an explicit allowlist of fields to server models; ignore unexpected
  properties such as `role`, `isAdmin` or `credit`.[^ch11]
* Validate types, ranges, lengths and formats against a schema (e.g. OpenAPI/JSON Schema).

## Safe interpreter use
* Use parameterised queries / prepared statements for SQL and the driver's safe operators
  for NoSQL; never build queries by string concatenation.[^ch12]
* Avoid passing user input to OS shells; if unavoidable, use argument arrays, not shell
  strings.
* Encode output for the context it lands in to prevent script injection downstream.

[^ch11]: Hacking APIs, Ch. 11 Mass Assignment, PDF pp. 265-276.
[^ch12]: Hacking APIs, Ch. 12 Injection, PDF pp. 277-292.
