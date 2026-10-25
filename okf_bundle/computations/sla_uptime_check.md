---
type: Attested Computation
title: Gateway SLA Uptime Calculation
description: Deterministic SQL computation verifying 99.95% gateway availability over a rolling 30 days.
status: stable
stale_after: "2027-01-01"
runtime: postgres
parameters:
  - name: region_code
    type: string
    required: true
executor:
  resource: "sql/run_sla_check.py"
  receipt: ["query_hash", "execution_timestamp", "uptime_pct"]
attester:
  resource: "verifiers/assert_sla_threshold.py"
verified:
  - by: "process:nightly-audit"
    at: "2026-10-20"
---
# Gateway SLA Uptime Calculation

Verifies regional gateway availability for the
[Zero Trust VPN Runbook](/runbooks/zero_trust_vpn.md). The attester fails the receipt if
`uptime_pct` is below 99.95.

Assumes one heartbeat row per gateway per minute, with `up_seconds` in the range 0–60.

# Computation
```sql
SELECT
  region_code,
  ROUND(100.0 * SUM(up_seconds) / (COUNT(*) * 60.0), 4) AS uptime_pct
FROM netops.gateway_heartbeats
WHERE region_code = :region_code
  AND check_time >= NOW() - INTERVAL '30 days'
GROUP BY region_code;
```
