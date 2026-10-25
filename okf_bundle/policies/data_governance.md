---
type: policy
title: Data Governance & PII Classification
description: Rules for handling sensitive customer PII and telemetry across staging and production.
status: stable
stale_after: "2026-12-31"
tags: ["compliance", "pii", "governance"]
verified:
  - by: "human:compliance_officer"
    at: "2026-07-20"
---
# Data Governance & PII Classification

Strict masking is enforced for all Tier-1 PII fields before ingestion into analytical or
RAG pipelines.

## Storage & access controls
* **Production access:** requires an active session governed by the
  [Remote Access Policy](/policies/remote_access.md).
* **Retention:** unmasked logs must be purged within 7 days.
