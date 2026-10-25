---
type: control
title: "Secure Configuration Control"
description: "Harden transport, headers, methods, defaults and logging across every deployment."
status: stable
stale_after: "2027-10-25"
tags: ["configuration", "headers", "tls", "control"]
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
# Secure Configuration Control

Prevents [Security Misconfiguration](/vulnerabilities/security_misconfiguration.md).

## Baseline
* TLS everywhere, including internal APIs; disable weak ciphers.[^ch3]
* Remove or neutralise revealing headers (`X-Powered-By`, server/version banners).[^ch7]
* Allow only required HTTP methods per route; disable `TRACE` and unused verbs.
* Remove default accounts and credentials before release.
* Ensure timing and error responses do not differ in ways that enumerate users or objects.
* Log authentication and authorization decisions and monitor for abuse.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch7]: Hacking APIs, Ch. 7 Endpoint Analysis, PDF pp. 183-206.
