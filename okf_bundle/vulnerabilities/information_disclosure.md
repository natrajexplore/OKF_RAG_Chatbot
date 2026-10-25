---
type: vulnerability
title: "Information Disclosure"
description: "APIs leak usernames, software versions, stack traces or internal paths useful for further attacks."
status: stable
stale_after: "2027-10-25"
tags: ["recon", "data-exposure"]
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
# Information Disclosure

Any unintended leak that helps plan a next step: user lists and slugs, verbose error
messages, stack traces, software and version banners, internal hostnames and paths.[^ch3]

## Where it appears
* Public user-listing endpoints (e.g. CMS user routes).
* Error responses that differ for "user exists" vs "wrong password".
* Response headers such as `X-Powered-By` — see [Security Misconfiguration](/vulnerabilities/security_misconfiguration.md).[^ch7]

## Prevent
Generic error messages, the [Response Filtering Control](/controls/response_filtering.md) and the [Secure Configuration Control](/controls/secure_configuration.md). Often the precursor to
[Broken Authentication](/vulnerabilities/broken_authentication.md) problems.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch7]: Hacking APIs, Ch. 7 Endpoint Analysis, PDF pp. 183-206.
