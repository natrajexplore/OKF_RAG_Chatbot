---
type: vulnerability
title: "Improper Assets Management"
description: "Old, test or undocumented API versions remain exposed and lack current protections."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api9", "inventory", "versioning"]
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
---
# Improper Assets Management

Retired (`/v1`), beta, staging or undocumented APIs stay reachable after the organisation
moves on. They often miss later fixes, making them the easiest path to [Excessive Data Exposure](/vulnerabilities/excessive_data_exposure.md),
[Mass Assignment](/vulnerabilities/mass_assignment.md) or [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md) problems.[^ch3]

## How it is discovered
Changelogs, old documentation, public repositories and version bumps in paths (`/v1` →
`/v2`, `/beta`, `/internal`) reveal candidates; recon tooling brute-forces them.[^ch6]
See [Attack-Surface Review](/runbooks/api_testing/recon_and_discovery.md).

## Prevent
The [API Inventory Control](/controls/api_inventory.md): maintain a living inventory, decommission old versions, and apply the same
gateway policy to every version.

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch6]: Hacking APIs, Ch. 6 Discovery, PDF pp. 151-182.
