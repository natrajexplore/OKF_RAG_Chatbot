---
type: control
title: "API Inventory Control"
description: "Maintain a living inventory of every API, version and environment, and retire old ones."
status: stable
stale_after: "2027-10-25"
tags: ["inventory", "versioning", "control"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch6
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 6 Discovery (PDF pp. 151-182)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
verified:
  - by: "human:appsec_lead"
    at: "2026-10-25"
---
# API Inventory Control

Prevents [Improper Assets Management](/vulnerabilities/improper_assets_management.md). The organisation keeps a current inventory of every API, version,
host and environment, with its owner and data classification.[^ch3]

## Implementation
* Decommission retired versions (`/v1`) rather than leaving them reachable.[^ch6]
* Gate staging, beta and internal APIs behind the same policy and authentication as prod.
* Reconcile the inventory against discovery scans so undocumented endpoints surface.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch6]: Hacking APIs, Ch. 6 Discovery, PDF pp. 151-182.
