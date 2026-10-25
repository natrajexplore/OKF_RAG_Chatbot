---
type: control
title: "Rate Limiting Control"
description: "Enforce server-side request limits on authentication and costly endpoints, keyed to identity."
status: stable
stale_after: "2027-10-25"
tags: ["rate-limiting", "availability", "control"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch13
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 13 Evasive Techniques and Rate Limit Testing (PDF pp. 295-312)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
verified:
  - by: "human:appsec_lead"
    at: "2026-10-25"
---
# Rate Limiting Control

Prevents [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md) abuse.

## Implementation
* Enforce limits server-side on login, password reset, token issuance and expensive
  queries; return `429` with `Retry-After`.[^ch3]
* Key limits on the authenticated identity and a trusted source signal, not on
  client-supplied headers like `X-Forwarded-For` that can be spoofed.[^ch13]
* Normalise the path before counting so case, trailing slashes or extra parameters cannot
  create separate buckets for the same handler.[^ch13]
* Add global quotas and alerting for sustained high volume.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch13]: Hacking APIs, Ch. 13 Evasive Techniques and Rate Limit Testing, PDF pp. 295-312.
