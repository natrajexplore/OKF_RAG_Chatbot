---
type: vulnerability
title: "Broken User Authentication"
description: "Weaknesses in login, token issuance, token handling or recovery that let attackers impersonate users."
status: stable
stale_after: "2027-10-25"
tags: ["owasp-api2", "authentication"]
sources:
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
  - id: ch8
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 8 Attacking Authentication (PDF pp. 207-228)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# Broken User Authentication

Any weakness in how an API proves identity: registration, login, password reset, MFA,
token generation and token handling.[^ch3] Because REST APIs are stateless, a leaked API
key or token is equivalent to a leaked username and password.

## Common weaknesses
* No lockout or rate limit on login, enabling credential guessing at scale
  (relates to [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md)).[^ch8]
* Predictable or low-entropy tokens.[^ch8]
* Tokens or API keys exposed in URLs, JavaScript bundles, public repositories or errors.
* Weak JSON Web Token validation — see [JWT Weaknesses](/vulnerabilities/jwt_attacks.md).
* Sensitive endpoints reachable with no authentication at all.

## Verify & prevent
Review with the [Authentication Assurance](/runbooks/api_testing/authentication_testing.md). Defend with the [Token Hardening Control](/controls/token_hardening.md) and the [Rate Limiting Control](/controls/rate_limiting.md).

[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
[^ch8]: Hacking APIs, Ch. 8 Attacking Authentication, PDF pp. 207-228.
