---
type: vulnerability
title: "Lack of Resources and Rate Limiting"
description: "Missing or bypassable request limits enable credential guessing, scraping, denial of service and cost abuse."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api4", "rate-limiting", "availability"]
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
---
# Lack of Resources and Rate Limiting

Rate limits protect availability, cost and monetisation. Without them, an API is open to
automated credential guessing, bulk scraping and resource exhaustion; for metered APIs,
evading limits directly costs the provider money.[^ch3]

## Ways limits are evaded (so you can test them)
* Spoofed client-IP headers (`X-Forwarded-For`, `X-Real-IP`) when the limiter trusts them.[^ch13]
* Path variations that reach the same handler under a different limiter key: case changes,
  trailing slashes, extra meaningless parameters.[^ch13]
* Rotating `Origin`/`User-Agent`, source IPs or accounts.[^ch13]

## Verify & prevent
Review with the [Rate-Limit Assurance](/runbooks/api_testing/evasion_and_rate_limit_testing.md). Defend with the [Rate Limiting Control](/controls/rate_limiting.md). Weak limits amplify [Broken Authentication](/vulnerabilities/broken_authentication.md).

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch13]: Hacking APIs, Ch. 13 Evasive Techniques and Rate Limit Testing, PDF pp. 295-312.
