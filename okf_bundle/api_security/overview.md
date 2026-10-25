---
type: overview
title: "API Security Knowledge Hub"
description: "Entry point to the API security bundle: weakness classes, assurance checklists and defensive controls."
status: stable
stale_after: "2027-10-25"
tags: ["api-security", "hub"]
sources:
  - id: ch2
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 2 The Anatomy of Web APIs (PDF pp. 55-80)"
    author: "Corey J. Ball"
  - id: ch3
    resource: "https://nostarch.com/hacking-apis"
    title: "Hacking APIs, Ch. 3 Common API Vulnerabilities (PDF pp. 81-96)"
    author: "Corey J. Ball"
generated:
  by: "claude-code/opus"
  at: "2026-10-25"
---
# API Security Knowledge Hub

Web APIs expose application logic and data directly to clients, so most weaknesses are
flaws in how the provider authenticates callers, authorizes each object and function, and
filters input and output.[^ch3] REST APIs are stateless: every request must carry its own
proof of identity (a token or API key), and the server must re-check that proof and the
caller's permissions on every request.[^ch2]

## Weakness classes
[BOLA](/vulnerabilities/bola.md) · [BFLA](/vulnerabilities/bfla.md) · [Broken Authentication](/vulnerabilities/broken_authentication.md) · [JWT Weaknesses](/vulnerabilities/jwt_attacks.md) · [Excessive Data Exposure](/vulnerabilities/excessive_data_exposure.md) · [Information Disclosure](/vulnerabilities/information_disclosure.md) ·
[Mass Assignment](/vulnerabilities/mass_assignment.md) · [Injection](/vulnerabilities/injection.md) · [Lack of Rate Limiting](/vulnerabilities/lack_of_rate_limiting.md) · [Security Misconfiguration](/vulnerabilities/security_misconfiguration.md) · [Improper Assets Management](/vulnerabilities/improper_assets_management.md) · [Business Logic Flaws](/vulnerabilities/business_logic_flaws.md) · [GraphQL Risks](/vulnerabilities/graphql_attacks.md)

## Assurance workflow (authorized reviews only)
[API Assurance Checklist](/runbooks/api_testing/api_hacking_checklist.md) covers the full sequence: [Attack-Surface Review](/runbooks/api_testing/recon_and_discovery.md) → [Endpoint Review](/runbooks/api_testing/endpoint_analysis.md) →
[Authentication Assurance](/runbooks/api_testing/authentication_testing.md) → [Authorization Assurance](/runbooks/api_testing/authorization_testing.md) → [Input Robustness Assurance](/runbooks/api_testing/fuzzing.md) → [Property Binding Assurance](/runbooks/api_testing/mass_assignment_testing.md) → [Injection Resistance Assurance](/runbooks/api_testing/injection_testing.md) →
[Rate-Limit Assurance](/runbooks/api_testing/evasion_and_rate_limit_testing.md) → [GraphQL Hardening Review](/runbooks/api_testing/graphql_testing.md).

## Defensive controls
[Object-Level Authorization Control](/controls/object_level_authorization.md) · [Function-Level Authorization Control](/controls/function_level_authorization.md) · [Token Hardening Control](/controls/token_hardening.md) · [Input Validation Control](/controls/input_validation.md) · [Response Filtering Control](/controls/response_filtering.md) · [Rate Limiting Control](/controls/rate_limiting.md) ·
[API Inventory Control](/controls/api_inventory.md) · [Secure Configuration Control](/controls/secure_configuration.md)

Governing policy: [API Security Policy](/policies/api_security_policy.md). Standards mapping: [OWASP API Top 10 (2023)](/standards/owasp_api_top10_2023.md).

[^ch2]: Hacking APIs, Ch. 2 The Anatomy of Web APIs, PDF pp. 55-80.
[^ch3]: Hacking APIs, Ch. 3 Common API Vulnerabilities, PDF pp. 81-96.
