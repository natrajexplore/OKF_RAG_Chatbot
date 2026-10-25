---
type: control
title: "Token Hardening Control"
description: "Issue, transmit, store and validate tokens so they cannot be forged, replayed or leaked."
status: stable
stale_after: "2027-10-25"
tags: ["authentication", "jwt", "tokens", "control"]
sources:
  - id: ch8
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 8 Attacking Authentication (PDF pp. 207-228)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
verified:
  - by: "human:appsec_lead"
    at: "2026-10-25"
---
# Token Hardening Control

Prevents [Broken Authentication](/vulnerabilities/broken_authentication.md) and [JWT Weaknesses](/vulnerabilities/jwt_attacks.md) issues.

## Issuance & validation
* Pin the expected signing algorithm server-side and reject `alg: none`.[^ch8]
* Use long, random secrets for HMAC, or asymmetric keys; never accept a token that selects
  its own algorithm.
* Always validate the signature and the `exp`, `iss` and `aud` claims.
* Use high-entropy, unpredictable token values.

## Handling
* Transmit only over TLS; send tokens in the `Authorization` header, never in URLs.
* Keep tokens out of client-side source, logs and error messages.
* Support rotation and revocation; keep lifetimes short.

[^ch8]: Hacking APIs, Ch. 8 Attacking Authentication, PDF pp. 207-228.
