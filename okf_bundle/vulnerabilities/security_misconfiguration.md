---
type: vulnerability
title: "Security Misconfiguration"
description: "Weak headers, missing TLS, default credentials, verbose errors and unnecessary HTTP methods."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api7", "configuration", "headers"]
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
# Security Misconfiguration

A catch-all for mistakes in the supporting configuration of an API.[^ch3]

## Examples
* **Revealing headers** — `X-Powered-By` with exact versions; disabled protections.
* **Timing differences** — response times that differ between existing and missing
  resources can enumerate users or objects.[^ch3]
* **No TLS** — even internal APIs can be intercepted on the network path.
* **Default accounts and credentials** left enabled.
* **Unneeded HTTP methods** (`PUT`, `DELETE`, `TRACE`) enabled on resources.
* **Verbose errors** exposing stack traces ([Information Disclosure](/vulnerabilities/information_disclosure.md)).[^ch7]

## Prevent
The [Secure Configuration Control](/controls/secure_configuration.md); many of these are detectable with standard configuration scanners.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch7]: Hacking APIs, Ch. 7 Endpoint Analysis, PDF pp. 183-206.
