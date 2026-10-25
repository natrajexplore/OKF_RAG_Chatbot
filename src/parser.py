"""Load an OKF v0.2 bundle into concept objects plus a NetworkX link graph.

Consumer rules (§11): unknown types/keys, broken links and missing optional fields are
tolerated. Files whose frontmatter cannot be parsed at all are skipped and reported in
`OKFBundle.load_errors` rather than crashing the app.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter
import networkx as nx

from src import okf_spec as spec


@dataclass
class OKFConcept:
    concept_id: str                 # e.g. "policies/remote_access"
    rel_path: str                   # e.g. "/policies/remote_access.md"
    title: str
    concept_type: str
    description: str
    status: str                     # absent in frontmatter => "stable" (§5.5)
    stale_after: str | None         # ISO date or None
    verified_by: list[str]
    trust_tier: str                 # unverified | machine-confirmed | human-reviewed
    body: str
    outbound_links: list[str]       # concept IDs that exist in the bundle
    broken_links: list[str]         # concept IDs referenced but missing
    raw_meta: dict[str, Any] = field(default_factory=dict)

    def is_stale(self, today=None) -> bool:
        return spec.is_stale(self.stale_after, today)


@dataclass
class OKFBundle:
    concepts: dict[str, OKFConcept]
    graph: nx.DiGraph
    load_errors: dict[str, str]


def _title_from_id(concept_id: str) -> str:
    return concept_id.rsplit("/", 1)[-1].replace("_", " ").replace("-", " ").title()


def load_okf_bundle(bundle_dir: Path) -> OKFBundle:
    bundle_dir = Path(bundle_dir)
    if not bundle_dir.is_dir():
        raise FileNotFoundError(f"OKF bundle directory not found: {bundle_dir}")

    concepts: dict[str, OKFConcept] = {}
    load_errors: dict[str, str] = {}
    pending_links: dict[str, list[str]] = {}

    for md_file in sorted(bundle_dir.rglob("*.md")):
        if md_file.name in spec.RESERVED_FILES:
            continue
        rel_path = "/" + md_file.relative_to(bundle_dir).as_posix()
        concept_id = spec.concept_id_from_rel_path(rel_path)
        try:
            post = frontmatter.load(md_file)
        except Exception as exc:  # unparseable YAML: skip, don't crash
            load_errors[rel_path] = str(exc)
            continue

        meta = dict(post.metadata)
        verified = spec.normalize_actor_events(meta.get("verified"))
        concepts[concept_id] = OKFConcept(
            concept_id=concept_id,
            rel_path=rel_path,
            title=str(meta.get("title") or _title_from_id(concept_id)),
            concept_type=str(meta.get("type") or "concept"),
            description=str(meta.get("description") or ""),
            status=spec.effective_status(meta),
            stale_after=spec.to_iso_date(meta.get("stale_after")),
            verified_by=[str(v.get("by", "unknown")) for v in verified],
            trust_tier=spec.trust_tier(verified),
            body=post.content,
            outbound_links=[],
            broken_links=[],
            raw_meta=meta,
        )
        pending_links[concept_id] = spec.extract_links(rel_path, post.content)

    graph = nx.DiGraph()
    for cid, c in concepts.items():
        graph.add_node(cid, title=c.title, type=c.concept_type, status=c.status)
    for cid, targets in pending_links.items():
        for target in targets:
            if target == cid:
                continue
            if target in concepts:
                concepts[cid].outbound_links.append(target)
                graph.add_edge(cid, target, relation="links_to")
            else:
                concepts[cid].broken_links.append(target)

    return OKFBundle(concepts=concepts, graph=graph, load_errors=load_errors)


def load_okf_knowledge_graph(bundle_dir: Path) -> tuple[dict[str, OKFConcept], nx.DiGraph]:
    """Backwards-compatible helper matching the original blueprint's signature."""
    bundle = load_okf_bundle(bundle_dir)
    return bundle.concepts, bundle.graph
