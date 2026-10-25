"""Backend tests for the FastAPI app. Fully offline: the hashing embedder avoids any model
download, and with no OLLAMA_MODEL/API keys the chat endpoint returns the offline synthesis.
The demo lab is pure in-memory logic."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    for var in ("GEMINI_API_KEY", "OPENAI_API_KEY", "OLLAMA_MODEL", "OKF_LLM", "CHROMA_PATH"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("OKF_EMBEDDING", "hash")  # no network, deterministic
    import src.api as api
    api._engine = None  # rebuild under the test env
    with TestClient(api.app) as c:
        yield c


def test_health_and_graph(client):
    h = client.get("/api/health").json()
    assert h["status"] == "ok" and h["provider"] == "offline"
    g = client.get("/api/graph").json()
    assert g["count"] == h["concepts"] >= 35
    assert g["link_count"] > 100


def test_chat_offline_cites_concepts(client):
    r = client.post("/api/chat", json={"query": "How do I prevent BOLA?",
                                       "top_k": 2, "hop_depth": 1}).json()
    assert "vulnerabilities/bola" in [c["concept_id"] for c in r["citations"]]
    assert "Offline synthesis" in r["answer"]  # no LLM configured
    # the deprecated OWASP 2019 standard, if retrieved, would be flagged; structure is present
    assert isinstance(r["trust_flags"], list)


def test_demo_bola_vulnerable_vs_secure(client):
    bad = client.post("/api/demo/bola",
                      json={"mode": "vulnerable",
                            "params": {"caller": "alice", "account_id": 5502}}).json()
    assert bad["attack_blocked"] is False          # alice read bob's account
    assert bad["response"]["account"]["owner"] == "bob"
    good = client.post("/api/demo/bola",
                       json={"mode": "secure",
                             "params": {"caller": "alice", "account_id": 5502}}).json()
    assert good["attack_blocked"] is True and good["response"]["status"] == 404


def test_demo_jwt_none_token(client):
    sample = client.get("/api/demo/jwt/sample").json()
    forged = sample["forged_none"]
    bad = client.post("/api/demo/jwt",
                      json={"mode": "vulnerable", "params": {"token": forged}}).json()
    assert bad["attack_blocked"] is False          # forged admin accepted
    good = client.post("/api/demo/jwt",
                       json={"mode": "secure", "params": {"token": forged}}).json()
    assert good["attack_blocked"] is True          # algorithm/signature rejected


def test_demo_mass_assignment_and_injection(client):
    bad = client.post("/api/demo/mass", json={"mode": "vulnerable", "params": {}}).json()
    assert bad["response"]["account"].get("isAdmin") is True
    good = client.post("/api/demo/mass", json={"mode": "secure", "params": {}}).json()
    assert good["response"]["account"]["role"] == "user"
    assert "isAdmin" in good["response"]["ignored_fields"]

    inj = client.post("/api/demo/injection",
                      json={"mode": "vulnerable", "params": {"name": "' OR '1'='1"}}).json()
    assert inj["attack_blocked"] is False          # concatenated query leaked rows
    safe = client.post("/api/demo/injection",
                       json={"mode": "secure", "params": {"name": "' OR '1'='1"}}).json()
    assert safe["attack_blocked"] is True


def test_demo_rate_limit_lockout(client):
    client.post("/api/demo/auth", json={"mode": "secure",
                                        "params": {"username": "alice", "password": "x", "reset": True}})
    last = None
    for _ in range(7):
        last = client.post("/api/demo/auth",
                           json={"mode": "secure",
                                 "params": {"username": "alice", "password": "x"}}).json()
    assert last["response"]["status"] == 429 and last["attack_blocked"] is True
