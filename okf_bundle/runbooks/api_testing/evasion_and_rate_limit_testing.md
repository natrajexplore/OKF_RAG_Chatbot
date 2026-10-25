---
type: runbook
title: "Rate-Limit Assurance"
description: "Confirm rate limits exist, are enforced server-side, and cannot be bypassed by trivial variation."
status: stable
stale_after: "2027-10-25"
tags: ["rate-limiting", "evasion"]
sources:
  - id: ch13
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 13 Evasive Techniques and Rate Limit Testing (PDF pp. 295-312)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Rate-Limit Assurance

Confirm limits exist and hold.[^ch13]

1. **Existence** — send a controlled burst to a limited endpoint and confirm `429`.
2. **Bypass resistance** — confirm limits are *not* defeated by:
   * spoofed `X-Forwarded-For`/`X-Real-IP` headers,
   * path variations (case, trailing slash, extra parameters),
   * rotating `Origin`/`User-Agent`.
3. **Keying** — confirm limits are keyed to identity and a trusted source signal.

Remediate with the [Rate Limiting Control](/controls/rate_limiting.md). Weak limits amplify [Broken Authentication](/vulnerabilities/broken_authentication.md).

[^ch13]: Hacking APIs, Ch. 13 Evasive Techniques and Rate Limit Testing, PDF pp. 295-312.
