from src.parser import load_okf_bundle


def test_sample_bundle_graph(sample_bundle):
    b = load_okf_bundle(sample_bundle)
    # Original enterprise-ops concepts are still present…
    assert {
        "policies/remote_access", "policies/data_governance",
        "runbooks/zero_trust_vpn", "computations/sla_uptime_check",
    } <= set(b.concepts)
    # …alongside the API-security knowledge base.
    assert {"api_security/overview", "vulnerabilities/bola",
            "controls/object_level_authorization",
            "runbooks/api_testing/api_hacking_checklist"} <= set(b.concepts)
    assert b.graph.has_edge("runbooks/zero_trust_vpn", "computations/sla_uptime_check")
    assert b.concepts["computations/sla_uptime_check"].concept_type == "Attested Computation"
    assert all(not c.broken_links for c in b.concepts.values())  # every link resolves
    assert not b.load_errors


def test_api_security_hub_links_resolve(sample_bundle):
    b = load_okf_bundle(sample_bundle)
    hub = b.concepts["api_security/overview"]
    # The hub links out to vulnerabilities, controls and runbooks, all resolvable.
    assert "vulnerabilities/bola" in hub.outbound_links
    assert "controls/token_hardening" in hub.outbound_links
    assert b.concepts["standards/owasp_api_top10_2019"].status == "deprecated"


def test_consumer_tolerance(make_bundle):
    root = make_bundle({
        "a.md": "---\ntype: whatever\nverified:\n  by: human:x\n  at: 2026-01-01\n---\n[b](/b.md) [gone](/gone.md)\n",
        "b.md": "---\ntype: note\nweird_key: 1\n---\nback to [a](a.md)\n",
        "bad.md": "---\ntype: [unclosed\n---\nbody\n",
    })
    b = load_okf_bundle(root)
    a = b.concepts["a"]
    assert a.status == "stable"                 # absent status => stable
    assert a.verified_by == ["human:x"]         # bare mapping accepted
    assert a.trust_tier == "human-reviewed"
    assert a.outbound_links == ["b"] and a.broken_links == ["gone"]
    assert b.graph.has_edge("b", "a")
    assert "/bad.md" in b.load_errors and "bad" not in b.concepts
