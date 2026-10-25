"""Secure-request demo lab.

A self-contained teaching sandbox. Each scenario has a `vulnerable` mode and a `secure`
mode so a visitor can see, side by side, how to maintain API requests securely. Everything
runs on throwaway in-memory data with fictional users — no real systems are touched.

Each function returns a dict the frontend renders:
  { ok, attack_blocked, request, response, explanation, control, concept }
`concept` is the OKF concept path that documents the fix.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sqlite3
import time
from typing import Any

# --- fictional data -------------------------------------------------------------
# owner -> account the caller legitimately owns; accounts keyed by id.
ACCOUNTS = {
    5501: {"id": 5501, "owner": "alice", "name": "Cloud Strife", "balance": 4200,
           "email": "cloud@example.test"},
    5502: {"id": 5502, "owner": "bob", "name": "Zack Fair", "balance": 9100,
           "email": "zack@example.test"},
}
USERS = {"alice": "correct-horse", "bob": "battery-staple"}
JWT_SECRET = b"demo-lab-shared-secret-change-me"

# login attempt counters for the rate-limit demo (reset via reset_login_state)
_login_attempts: dict[str, list[float]] = {}
LOCKOUT_LIMIT = 5
LOCKOUT_WINDOW = 60.0


def _result(ok: bool, blocked: bool, request: Any, response: Any,
            explanation: str, control: str, concept: str) -> dict:
    return {"ok": ok, "attack_blocked": blocked, "request": request, "response": response,
            "explanation": explanation, "control": control, "concept": concept}


# --- 1. BOLA (object-level authorization) ---------------------------------------
def bola(mode: str, caller: str, account_id: int) -> dict:
    req = {"method": "GET", "path": f"/accounts/{account_id}", "as_user": caller}
    acct = ACCOUNTS.get(account_id)
    if acct is None:
        return _result(True, True, req, {"status": 404}, "No such account.",
                       "Object-Level Authorization", "vulnerabilities/bola")
    if mode == "secure":
        if acct["owner"] != caller:
            # same 404 whether missing or not-owned, so existence does not leak
            return _result(True, True, req, {"status": 404},
                           f"Secure: '{caller}' does not own account {account_id}, so the "
                           "server returns 404 and reveals nothing.",
                           "Object-Level Authorization", "vulnerabilities/bola")
        return _result(True, False, req, {"status": 200, "account": acct},
                       f"Secure: '{caller}' owns account {account_id}, access granted.",
                       "Object-Level Authorization", "vulnerabilities/bola")
    # vulnerable: returns the object without checking ownership
    leaked = acct["owner"] != caller
    return _result(True, not leaked, req, {"status": 200, "account": acct},
                   ("Vulnerable: the server never checked ownership, so '%s' just read "
                    "%s's account — a BOLA." % (caller, acct["owner"])) if leaked else
                   f"'{caller}' read their own account (no check performed, but same owner).",
                   "Object-Level Authorization", "vulnerabilities/bola")


# --- 2. Broken auth + rate limiting (login) -------------------------------------
def reset_login_state() -> None:
    _login_attempts.clear()


def login(mode: str, username: str, password: str) -> dict:
    req = {"method": "POST", "path": "/login", "body": {"username": username,
           "password": "********"}}
    now = time.time()
    hits = [t for t in _login_attempts.get(username, []) if now - t < LOCKOUT_WINDOW]
    if mode == "secure" and len(hits) >= LOCKOUT_LIMIT:
        return _result(True, True, req,
                       {"status": 429, "error": "Too many attempts. Try again later.",
                        "attempts_in_window": len(hits)},
                       "Secure: repeated failures are throttled (HTTP 429), so credential "
                       "guessing cannot run at scale.",
                       "Rate Limiting", "vulnerabilities/broken_authentication")
    valid = USERS.get(username) == password
    if not valid:
        hits.append(now)
        _login_attempts[username] = hits
        blocked = mode == "secure"
        return _result(True, blocked, req,
                       {"status": 401, "error": "Invalid credentials",
                        "attempts_in_window": len(hits),
                        "rate_limited": mode == "secure"},
                       ("Vulnerable: every failed attempt is accepted with no limit, so an "
                        "attacker can keep guessing." if mode == "vulnerable" else
                        f"Secure: attempt {len(hits)} of {LOCKOUT_LIMIT} before lockout."),
                       "Rate Limiting", "vulnerabilities/broken_authentication")
    _login_attempts[username] = []
    return _result(True, False, req, {"status": 200, "token": "demo-session-token"},
                   "Login succeeded.", "Rate Limiting",
                   "vulnerabilities/broken_authentication")


# --- 3. JWT validation ----------------------------------------------------------
def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(seg: str) -> bytes:
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def issue_jwt(username: str, role: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": username, "role": role, "exp": int(time.time()) + 3600}
    signing_input = f"{_b64url(json.dumps(header).encode())}.{_b64url(json.dumps(payload).encode())}"
    sig = hmac.new(JWT_SECRET, signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url(sig)}"


def verify_jwt(mode: str, token: str) -> dict:
    req = {"method": "GET", "path": "/admin/metrics", "authorization": f"Bearer {token[:24]}…"}
    try:
        h_seg, p_seg, sig_seg = token.split(".")
        header = json.loads(_b64url_decode(h_seg))
        payload = json.loads(_b64url_decode(p_seg))
    except Exception:
        return _result(True, True, req, {"status": 400, "error": "Malformed token"},
                       "Token could not be parsed.", "Token Hardening",
                       "vulnerabilities/jwt_attacks")
    alg = header.get("alg", "")
    if mode == "secure":
        if alg != "HS256":
            return _result(True, True, req,
                           {"status": 401, "error": f"Algorithm '{alg}' rejected"},
                           "Secure: the server pins HS256 and rejects any other algorithm "
                           "(including 'none'), so a tampered header is refused.",
                           "Token Hardening", "vulnerabilities/jwt_attacks")
        signing_input = f"{h_seg}.{p_seg}"
        expected = hmac.new(JWT_SECRET, signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(sig_seg)):
            return _result(True, True, req, {"status": 401, "error": "Bad signature"},
                           "Secure: the signature did not verify, so the forged claims are "
                           "rejected.", "Token Hardening", "vulnerabilities/jwt_attacks")
        return _result(True, False, req, {"status": 200, "claims": payload},
                       f"Secure: valid HS256 token for '{payload.get('sub')}' "
                       f"(role {payload.get('role')}).",
                       "Token Hardening", "vulnerabilities/jwt_attacks")
    # vulnerable: trusts the header, skips signature verification
    granted = payload.get("role") == "admin"
    return _result(True, not granted, req, {"status": 200 if granted else 403, "claims": payload},
                   f"Vulnerable: the server trusted alg='{alg}' and the claims without "
                   f"verifying the signature, so role='{payload.get('role')}' was accepted "
                   "as-is — a forged admin token would pass.",
                   "Token Hardening", "vulnerabilities/jwt_attacks")


# --- 4. Mass assignment ---------------------------------------------------------
ALLOWED_REGISTER_FIELDS = {"username", "password"}


def register(mode: str, payload: dict) -> dict:
    req = {"method": "POST", "path": "/users", "body": {**payload,
           **({"password": "********"} if "password" in payload else {})}}
    if mode == "secure":
        clean = {k: v for k, v in payload.items() if k in ALLOWED_REGISTER_FIELDS}
        account = {"username": clean.get("username"), "role": "user"}  # role forced server-side
        ignored = sorted(set(payload) - ALLOWED_REGISTER_FIELDS)
        return _result(True, bool(ignored) or True, req,
                       {"status": 201, "account": account, "ignored_fields": ignored},
                       "Secure: only allow-listed fields are bound; "
                       + (f"ignored client-supplied {ignored}." if ignored else
                          "no extra fields were sent."),
                       "Input Validation", "vulnerabilities/mass_assignment")
    account = {"username": payload.get("username"), "role": "user"}
    account.update({k: v for k, v in payload.items() if k not in ("username", "password")})
    escalated = account.get("role") == "admin" or account.get("isAdmin") is True
    return _result(True, not escalated, req, {"status": 201, "account": account},
                   ("Vulnerable: the whole body was bound onto the account, so the caller set "
                    "privileged fields and became an admin — mass assignment." if escalated else
                    "Vulnerable: the whole body was bound, but no privileged field was sent."),
                   "Input Validation", "vulnerabilities/mass_assignment")


# --- 5. Injection (SQL) ---------------------------------------------------------
def _seed_db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users (id INTEGER, name TEXT, secret TEXT)")
    con.executemany("INSERT INTO users VALUES (?,?,?)",
                    [(1, "Cloud Strife", "public"), (2, "Zack Fair", "public"),
                     (3, "admin", "TOP-SECRET-FLAG")])
    con.commit()
    return con


def search(mode: str, query: str) -> dict:
    req = {"method": "GET", "path": "/users/search", "query": {"name": query}}
    con = _seed_db()
    try:
        if mode == "secure":
            rows = con.execute(
                "SELECT id, name FROM users WHERE name = ?", (query,)).fetchall()
            data = [{"id": r[0], "name": r[1]} for r in rows]
            return _result(True, True, req, {"status": 200, "results": data},
                           "Secure: the input is bound as a parameter, so metacharacters are "
                           "treated as data — no injection is possible.",
                           "Input Validation", "vulnerabilities/injection")
        # vulnerable: string-concatenated query on a throwaway in-memory table
        sql = f"SELECT id, name, secret FROM users WHERE name = '{query}'"
        try:
            rows = con.execute(sql).fetchall()
        except sqlite3.Error as exc:
            return _result(True, False, req, {"status": 500, "error": str(exc), "sql": sql},
                           "Vulnerable: the input was concatenated into the SQL string, so a "
                           "crafted value changed the query and produced a database error — a "
                           "classic injection signal.",
                           "Input Validation", "vulnerabilities/injection")
        leaked_secret = any(len(r) > 2 and r[2] != "public" for r in rows)
        data = [{"id": r[0], "name": r[1], "secret": r[2]} for r in rows]
        return _result(True, not leaked_secret, req,
                       {"status": 200, "results": data, "sql": sql},
                       ("Vulnerable: the concatenated query was manipulated to return rows the "
                        "request should never see, including a secret value — SQL injection."
                        if leaked_secret else
                        "Vulnerable query ran; this input happened not to leak extra rows."),
                       "Input Validation", "vulnerabilities/injection")
    finally:
        con.close()


SCENARIOS = {
    "bola": {"title": "Broken Object Level Authorization",
             "concept": "vulnerabilities/bola",
             "blurb": "Read another user's account by changing the ID."},
    "auth": {"title": "Broken Authentication & Rate Limiting",
             "concept": "vulnerabilities/broken_authentication",
             "blurb": "Guess a password repeatedly with and without a rate limit."},
    "jwt": {"title": "JWT Validation",
            "concept": "vulnerabilities/jwt_attacks",
            "blurb": "Present a tampered 'none'-algorithm token to an admin endpoint."},
    "mass": {"title": "Mass Assignment",
             "concept": "vulnerabilities/mass_assignment",
             "blurb": "Send an extra isAdmin field during registration."},
    "injection": {"title": "SQL Injection",
                  "concept": "vulnerabilities/injection",
                  "blurb": "Send a crafted search value to a concatenated query."},
}
