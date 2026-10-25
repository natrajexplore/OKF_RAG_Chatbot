import datetime as dt

from src import okf_spec as spec


def test_stale_boundary_is_inclusive():
    today = dt.date(2026, 10, 25)
    assert spec.is_stale("2026-10-25", today)          # today >= stale_after -> stale
    assert spec.is_stale(dt.date(2026, 1, 1), today)
    assert not spec.is_stale("2026-10-26", today)
    assert not spec.is_stale(None, today)
    assert not spec.is_stale("not-a-date", today)


def test_bare_verified_mapping_is_one_element_list():
    assert spec.normalize_actor_events({"by": "human:a"}) == [{"by": "human:a"}]
    assert spec.normalize_actor_events(None) == []
    assert spec.trust_tier({"by": "human:a"}) == "human-reviewed"
    assert spec.trust_tier([{"by": "process:nightly"}]) == "machine-confirmed"
    assert spec.trust_tier(None) == "unverified"


def test_absent_status_means_stable():
    assert spec.effective_status({}) == "stable"
    assert spec.effective_status({"status": "draft"}) == "draft"


def test_resolve_link_absolute_relative_and_escape():
    src = "/runbooks/vpn.md"
    assert spec.resolve_link(src, "/policies/a.md") == "policies/a"
    assert spec.resolve_link(src, "../policies/a.md") == "policies/a"
    assert spec.resolve_link(src, "./sibling.md") == "runbooks/sibling"
    assert spec.resolve_link(src, "../../outside.md") is None
    assert spec.resolve_link(src, "https://example.com/x.md") is None


def test_extract_links_handles_fragments_images_and_code_fences():
    body = (
        "See [A](/a.md#section) and [B](./b.md) and [A again](/a.md).\n"
        "![diagram](/img/diagram.md)\n"
        "```\n[not a link](/c.md)\n```\n"
        "External [x](https://site/x.md)."
    )
    assert spec.extract_links("/dir/src.md", body) == ["a", "dir/b"]
