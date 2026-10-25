---
type: control
title: "Response Filtering Control"
description: "Shape responses server-side to the exact fields each role needs; never serialise raw objects."
status: stable
stale_after: "2027-10-25"
tags: ["data-exposure", "pii", "control"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch7
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 7 Endpoint Analysis (PDF pp. 183-206)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
verified:
  - by: "human:appsec_lead"
    at: "2026-10-25"
---
# Response Filtering Control

Prevents [Excessive Data Exposure](/vulnerabilities/excessive_data_exposure.md) and [Information Disclosure](/vulnerabilities/information_disclosure.md). The server decides what each role sees; it never
relies on the client to hide fields.[^ch3]

## Implementation
* Define explicit response schemas (DTOs) per endpoint and role; do not return ORM or
  database objects directly.[^ch7]
* Exclude internal fields: password hashes, other users' records, internal IDs, debug flags.
* Use generic error messages; keep stack traces and version banners out of responses.
* PII in responses is additionally governed by the [Data Governance Policy](/policies/data_governance.md).

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch7]: Hacking APIs, Ch. 7 Endpoint Analysis, PDF pp. 183-206.
