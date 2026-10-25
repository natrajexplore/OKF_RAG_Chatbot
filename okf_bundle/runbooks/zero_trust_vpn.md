---
type: runbook
title: Zero Trust VPN Triage & Setup Runbook
description: Step-by-step diagnostic procedure for resolving mTLS certificate and tunnel drops.
status: stable
stale_after: "2027-03-15"
resource: "urn:corp:net:zt-gateway-01"
tags: ["network", "triage", "mtls", "vpn"]
generated:
  by: "human:netops_team"
  at: "2026-08-20"
verified:
  - by: "human:principal_net_eng"
    at: "2026-09-10"
---
# Zero Trust VPN Triage & Setup Runbook

This runbook covers the connectivity required by the
[Remote Access Policy](/policies/remote_access.md).

## Diagnostic steps
1. **Verify the mTLS certificate:** run `certutil -store My` (Windows) or inspect the client
   keychain to confirm the certificate issued by the Root CA has not expired.
2. **Check UDP 443 / 41641:** ensure local firewall rules allow outbound QUIC/WireGuard handshakes.
3. **Verify gateway SLA:** if handshake timeouts persist across multiple regions, run the
   [Gateway SLA Uptime Check](/computations/sla_uptime_check.md) to confirm gateway availability.
