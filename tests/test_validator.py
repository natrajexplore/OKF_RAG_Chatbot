import datetime as dt

from src.validator import main, validate_okf_bundle

TODAY = dt.date(2026, 10, 25)


def _by_path(results):
    return {r.path: r for r in results}


def test_sample_bundle_has_zero_errors(sample_bundle):
    results = validate_okf_bundle(sample_bundle, today=TODAY)
    assert sum(len(r.errors) for r in results) == 0, [(r.path, r.errors) for r in results]
    assert main([str(sample_bundle)]) == 0


def test_missing_frontmatter_and_type_are_errors(make_bundle):
    root = make_bundle({
        "index.md": '---\nokf_version: "0.2"\n---\n# Root\n',
        "a.md": "# No frontmatter\n",
        "b.md": "---\ntitle: No type\n---\nbody\n",
    })
    res = _by_path(validate_okf_bundle(root, today=TODAY))
    assert any("missing YAML frontmatter" in e for e in res["/a.md"].errors)
    assert any("`type`" in e for e in res["/a.md"].errors)
    assert any("`type`" in e for e in res["/b.md"].errors)
    assert main([str(root)]) == 1


def test_only_root_index_may_carry_frontmatter(make_bundle):
    root = make_bundle({
        "index.md": '---\nokf_version: "0.2"\ntitle: nope\n---\n',
        "sub/index.md": "---\nokf_version: \"0.2\"\n---\n# Sub index\n",
    })
    res = _by_path(validate_okf_bundle(root, today=TODAY))
    assert res["/index.md"].errors      # extra key on root index
    assert res["/sub/index.md"].errors  # nested index with frontmatter


def test_attested_computation_rules(make_bundle):
    root = make_bundle({
        "c1.md": "---\ntype: Attested Computation\n---\nbody\n",
        "c2.md": "---\ntype: attested_computation\nruntime: postgres\n---\nbody\n",
    })
    res = _by_path(validate_okf_bundle(root, today=TODAY))
    assert any("runtime" in e for e in res["/c1.md"].errors)
    assert any("exact" in w for w in res["/c2.md"].warnings)
    assert res["/c2.md"].valid  # unknown type is not an error (§11)


def test_trust_lifecycle_provenance_and_links_are_warnings(make_bundle):
    root = make_bundle({
        "a.md": """
            ---
            type: policy
            status: retired
            stale_after: "2026-10-25"
            sources:
              - uri: https://x
            generated:
              by: somebody
            ---
            Links to [missing](/nope.md).[^ghost]
            """,
    })
    r = _by_path(validate_okf_bundle(root, today=TODAY))["/a.md"]
    assert r.valid
    text = " ".join(r.warnings)
    for needle in ("draft | stable | deprecated", "STALE", "resource", "actor convention",
                   "Broken link", "no `verified`"):
        assert needle in text, needle
    assert main([str(root), "--strict"]) == 1


def test_log_md_must_be_iso_and_newest_first(make_bundle):
    root = make_bundle({"log.md": "# Log\n\n## 2026-01-01\n* a\n\n## 2026-05-01\n* b\n\n## May 2\n"})
    r = _by_path(validate_okf_bundle(root, today=TODAY))["/log.md"]
    assert any("ISO" in w for w in r.warnings)
    assert any("newest first" in w for w in r.warnings)
