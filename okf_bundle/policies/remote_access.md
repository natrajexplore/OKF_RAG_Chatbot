---
type: policy
title: Enterprise Remote Access Policy
description: Mandatory zero-trust authentication and split-tunnel rules for remote engineers.
status: stable
stale_after: "2027-06-30"
tags: ["security", "vpn", "zero-trust"]
sources:
  - id: infosec-charter
    resource: "https://internal.corp/sec-charter-2026.pdf"
    title: "InfoSec Charter 2026, Section 4.2"
generated:
  by: "gemini/2.5-pro"
  at: "2026-08-15"
verified:
  - by: "human:sec_lead"
    at: "2026-09-01"
---
# Enterprise Remote Access Policy

All remote engineering sessions touching production clusters must authenticate through
the Zero Trust gateway.[^infosec-charter]

## Mandatory requirements
1. **Device posture check:** endpoints must pass EDR verification before a tunnel is established.
2. **Tunnel protocol:** legacy IPsec profiles are deprecated. Engineers configure the client
   per the [Zero Trust VPN Runbook](/runbooks/zero_trust_vpn.md).
3. **Data handling:** customer telemetry accessed remotely is subject to the
   [Data Governance Policy](/policies/data_governance.md).

[^infosec-charter]: InfoSec Charter 2026, Section 4.2
