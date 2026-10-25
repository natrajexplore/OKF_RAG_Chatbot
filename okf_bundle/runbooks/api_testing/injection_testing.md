---
type: runbook
title: "Injection Resistance Assurance"
description: "Confirm user input cannot reach backend interpreters as code."
status: stable
stale_after: "2027-10-25"
tags: ["injection", "sqli"]
sources:
  - id: ch12
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 12 Injection (PDF pp. 277-292)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Injection Resistance Assurance

For every parameter that accepts user input, confirm it cannot alter a backend query or
command.[^ch12]

* Submit benign metacharacters (`'`, `"`, `;`, `--`, `$ne`, `|`) and watch for errors,
  changed result counts or timing shifts that signal [Injection](/vulnerabilities/injection.md).
* Cover SQL, NoSQL, OS-command, template and path-traversal contexts.
* Confirm responses do not render injected values unescaped downstream.

Remediate with the [Input Validation Control](/controls/input_validation.md): parameterised queries, safe operators, output encoding.

[^ch12]: Hacking APIs, Ch. 12 Injection, PDF pp. 277-292.
