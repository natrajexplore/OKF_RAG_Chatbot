---
type: runbook
title: "Attack-Surface Review"
description: "Enumerate APIs, versions and documentation to build an authoritative endpoint inventory."
status: stable
stale_after: "2027-10-25"
tags: ["recon", "discovery"]
sources:
  - id: ch6
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 6 Discovery (PDF pp. 151-182)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Attack-Surface Review

Goal: know every endpoint and version in scope before testing behaviour.[^ch6]

## Passive
* Search for exposed OpenAPI/Swagger files, documentation and leaked keys in public sources.
* Review public code repositories and changelogs for endpoints, versions and secrets.

## Active (in scope only)
* Baseline service scan of in-scope hosts.[^ch6]
* Observe the API calls a web client makes via browser developer tools.
* Crawl through an intercepting proxy; enumerate paths (including version prefixes) with
  API-aware wordlists to surface [Improper Assets Management](/vulnerabilities/improper_assets_management.md).

## Output
An endpoint inventory feeding the [Endpoint Review](/runbooks/api_testing/endpoint_analysis.md). Note any [Information Disclosure](/vulnerabilities/information_disclosure.md) found en route.

[^ch6]: Hacking APIs, Ch. 6 Discovery, PDF pp. 151-182.
