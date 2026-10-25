---
type: vulnerability
title: "JSON Web Token (JWT) Weaknesses"
description: "JWTs can be forged or tampered when the server trusts the token's own algorithm header or uses a weak secret."
status: stable
stale_after: "2027-10-25"
tags: ["authentication", "jwt", "tokens"]
sources:
  - id: ch8
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 8 Attacking Authentication (PDF pp. 207-228)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# JSON Web Token (JWT) Weaknesses

A JWT is `header.payload.signature`, each part base64url-encoded. The header names the
signing algorithm; the payload holds claims such as `sub`, `role` and `exp`. The payload is
*encoded, not encrypted* — anyone holding the token can read it.[^ch8]

## Weakness families
* **`alg: none`** — a server that trusts the header and skips verification will accept an
  unsigned, edited token.[^ch8]
* **Algorithm confusion** — switching an asymmetric algorithm to an HMAC one so a public
  key is mistaken for a shared secret, when the library lets the token choose.[^ch8]
* **Weak secret** — a short HMAC secret can be recovered offline from one captured token,
  after which claims can be forged.[^ch8]
* **Unverified claims** — changing `role` or `sub` when the signature is not checked.

## Prevent
Apply the [Token Hardening Control](/controls/token_hardening.md): pin the expected algorithm server-side, reject `none`, use strong
secrets or asymmetric keys, and validate `exp`, `iss` and `aud`. Part of [Broken Authentication](/vulnerabilities/broken_authentication.md).

[^ch8]: Hacking APIs, Ch. 8 Attacking Authentication, PDF pp. 207-228.
