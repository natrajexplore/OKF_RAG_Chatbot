---
type: vulnerability
title: "Mass Assignment"
description: "The API binds extra client-supplied properties (e.g. isAdmin) directly onto server objects."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api6", "input", "authorization"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch11
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 11 Mass Assignment (PDF pp. 265-276)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Mass Assignment

Frameworks that bind a whole request body onto a model let callers set properties they were
never meant to control. Sending `{"user": "x", "password": "…", "isAdmin": true}` creates
an administrator if the server does not filter fields.[^ch3]

## Candidate fields to look for
* Fields seen in responses but not requests (`role`, `credit`, `verified`, `org_id`).[^ch11]
* Admin documentation and older API versions ([Improper Assets Management](/vulnerabilities/improper_assets_management.md)).

## Verify & prevent
Review with the [Property Binding Assurance](/runbooks/api_testing/mass_assignment_testing.md). Prevent with the [Input Validation Control](/controls/input_validation.md) (allowlisted, typed request
schemas). In the 2023 OWASP list this falls under property-level authorization ([OWASP API Top 10 (2023)](/standards/owasp_api_top10_2023.md)).

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch11]: Hacking APIs, Ch. 11 Mass Assignment, PDF pp. 265-276.
