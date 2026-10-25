---
type: runbook
title: "Authentication Assurance"
description: "Verify login, token issuance and token validation resist guessing and tampering."
status: stable
stale_after: "2027-10-25"
tags: ["authentication", "jwt"]
sources:
  - id: ch8
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 8 Attacking Authentication (PDF pp. 207-228)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Authentication Assurance

Confirm each item holds; any failure maps to [Broken Authentication](/vulnerabilities/broken_authentication.md) or [JWT Weaknesses](/vulnerabilities/jwt_attacks.md).[^ch8]

1. **Lockout / throttling** — login, reset and token endpoints enforce limits (ties to
   the [Rate Limiting Control](/controls/rate_limiting.md)).
2. **Token entropy** — issued tokens are long and unpredictable.
3. **No secrets in the wrong place** — tokens/keys are absent from URLs, client code, logs.
4. **JWT validation** — server pins the algorithm, rejects `none`, verifies the signature
   and `exp`/`iss`/`aud`, and uses a strong secret or asymmetric keys.
5. **Unauthenticated access** — sensitive endpoints reject anonymous callers.

Remediate with the [Token Hardening Control](/controls/token_hardening.md).

[^ch8]: Hacking APIs, Ch. 8 Attacking Authentication, PDF pp. 207-228.
