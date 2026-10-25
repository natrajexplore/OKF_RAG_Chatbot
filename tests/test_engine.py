import datetime as dt

import pytest

from src.engine import OKFHybridRAGEngine


@pytest.fixture
def engine(sample_bundle, embedding_fn, monkeypatch):
    for var in ("GEMINI_API_KEY", "OPENAI_API_KEY", "CHROMA_PATH", "OLLAMA_MODEL", "OKF_LLM"):
        monkeypatch.delenv(var, raising=False)
    return OKFHybridRAGEngine(sample_bundle, embedding_function=embedding_fn)


def test_semantic_seed_then_graph_expansion(engine):
    r = engine.retrieve_with_graph_expansion("mTLS certificate tunnel drops triage", top_k=1, hop_depth=1)
    assert r.seed_ids == ["runbooks/zero_trust_vpn"]
    assert set(r.expanded_ids) == {"policies/remote_access", "computations/sla_uptime_check"}
    assert any("->" in p for p in r.traversal_paths)
    assert [c.concept_id for c in r.concepts][0] == "runbooks/zero_trust_vpn"


def test_two_hops_reaches_data_governance_with_path(engine):
    r = engine.retrieve_with_graph_expansion("mTLS certificate tunnel drops triage", top_k=1, hop_depth=2)
    assert "policies/data_governance" in r.expanded_ids
    path = r.traversal_paths[r.expanded_ids.index("policies/data_governance")]
    assert path.count("->") + path.count("<-") == 2


def test_zero_hops_means_no_expansion(engine):
    r = engine.retrieve_with_graph_expansion("PII masking retention", top_k=1, hop_depth=0)
    assert r.expanded_ids == [] and len(r.concepts) == 1


def test_independent_instances_do_not_share_collections(sample_bundle, embedding_fn):
    e1 = OKFHybridRAGEngine(sample_bundle, embedding_function=embedding_fn)
    e2 = OKFHybridRAGEngine(sample_bundle, embedding_function=embedding_fn)
    assert e1.collection.name != e2.collection.name
    assert e1.collection.count() == e2.collection.count() == len(e1.concepts)


def test_api_security_retrieval_finds_bola(engine):
    r = engine.retrieve_with_graph_expansion(
        "broken object level authorization IDOR access another user's account",
        top_k=2, hop_depth=1)
    assert "vulnerabilities/bola" in r.seed_ids
    # BOLA links to its prevention control, reached by graph expansion.
    assert "controls/object_level_authorization" in (r.seed_ids + r.expanded_ids)


def test_ollama_provider_selected_and_mocked(engine, monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "nemotron-3-nano:4b")
    captured = {}

    def fake(system_prompt, user_message):
        captured["system"] = system_prompt
        captured["user"] = user_message
        return "Grounded answer citing [/vulnerabilities/bola.md]."

    monkeypatch.setattr(engine, "_answer_ollama", fake)
    r = engine.retrieve_with_graph_expansion("What is BOLA?", top_k=1, hop_depth=0)
    answer = engine.answer_query("What is BOLA?", r)
    assert "bola.md" in answer
    assert "OKF" in captured["user"]  # context was passed through


def test_context_prompt_flags_stale(engine):
    concepts = [engine.concepts["policies/data_governance"]]   # stale_after 2026-12-31
    ctx = engine.format_okf_context_prompt(concepts, today=dt.date(2027, 1, 1))
    assert "STALE" in ctx and "HUMAN-REVIEWED" in ctx


def test_offline_answer_without_keys(engine):
    r = engine.retrieve_with_graph_expansion("VPN", top_k=2, hop_depth=1)
    answer = engine.answer_query("VPN", r)
    assert "Offline synthesis" in answer and "/runbooks/zero_trust_vpn.md" in answer
