---
type: vulnerability
title: "Excessive Data Exposure"
description: "Endpoints return more fields or records than the client needs, trusting the client to filter them."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api3", "data-exposure", "pii"]
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
---
# Excessive Data Exposure

The API returns full internal objects and relies on the front end to hide what users
should not see.[^ch3] A request for one's own profile might also return a linked admin's
email, privilege level and MFA status. Because the data is *legitimately returned*, it
slips past other controls.

## Recognise it
Read raw responses, not the rendered UI, and look for extra fields, other users' records,
internal IDs, hashes or flags ([Endpoint Review](/runbooks/api_testing/endpoint_analysis.md)).[^ch7]

## Prevent
Apply the [Response Filtering Control](/controls/response_filtering.md): explicit per-role response schemas; never serialise database
objects directly. Exposed PII also falls under the [Data Governance Policy](/policies/data_governance.md). Closely related to [Information Disclosure](/vulnerabilities/information_disclosure.md).

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch7]: Hacking APIs, Ch. 7 Endpoint Analysis, PDF pp. 183-206.
