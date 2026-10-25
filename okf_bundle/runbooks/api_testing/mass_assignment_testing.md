---
type: runbook
title: "Property Binding Assurance"
description: "Confirm the API ignores client-supplied properties the caller should not control."
status: stable
stale_after: "2027-10-25"
tags: ["mass-assignment", "input"]
sources:
  - id: ch11
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 11 Mass Assignment (PDF pp. 265-276)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Property Binding Assurance

Confirm the API binds only intended fields.[^ch11]

* Collect candidate privileged fields from responses, admin docs and older versions
  ([Improper Assets Management](/vulnerabilities/improper_assets_management.md)): `role`, `isAdmin`, `credit`, `verified`, `org_id`.
* Add each to create/update requests and confirm the server ignores it (value unchanged).
* A field that takes effect indicates [Mass Assignment](/vulnerabilities/mass_assignment.md).

Remediate with the [Input Validation Control](/controls/input_validation.md) (allowlisted request schemas).

[^ch11]: Hacking APIs, Ch. 11 Mass Assignment, PDF pp. 265-276.
