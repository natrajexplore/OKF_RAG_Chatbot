---
type: runbook
title: "Input Robustness Assurance"
description: "Send malformed, boundary and unexpected inputs and confirm the API fails safely."
status: stable
stale_after: "2027-10-25"
tags: ["fuzzing", "robustness"]
sources:
  - id: ch9
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 9 Fuzzing (PDF pp. 229-250)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Input Robustness Assurance

Send unexpected input across every parameter and confirm the API validates and fails
safely rather than erroring verbosely or misbehaving.[^ch9]

* Use wordlists of unexpected values, boundary sizes, wrong types and metacharacters.
* Watch for `500`s, verbose errors, stack traces and inconsistent status codes — these can
  indicate [Injection](/vulnerabilities/injection.md) or [Security Misconfiguration](/vulnerabilities/security_misconfiguration.md).
* Feed interesting fields into the [Property Binding Assurance](/runbooks/api_testing/mass_assignment_testing.md) and [Injection Resistance Assurance](/runbooks/api_testing/injection_testing.md).

Remediate with the [Input Validation Control](/controls/input_validation.md) and the [Secure Configuration Control](/controls/secure_configuration.md).

[^ch9]: Hacking APIs, Ch. 9 Fuzzing, PDF pp. 229-250.
