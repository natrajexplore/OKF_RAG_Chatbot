"""Streamlit workbench: hybrid RAG chat, concept-graph inspector, conformance audit.

Run from the project root:  uv run streamlit run src/app.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# `streamlit run src/app.py` puts src/ (not the project root) on sys.path,
# so `import src.*` would fail without this.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402

from src.engine import OKFHybridRAGEngine  # noqa: E402
from src.validator import validate_okf_bundle  # noqa: E402

BUNDLE_PATH = Path(os.getenv("OKF_BUNDLE_PATH", PROJECT_ROOT / "okf_bundle"))

st.set_page_config(page_title="OKF v0.2 Hybrid RAG", layout="wide")
st.title("Open Knowledge Format (OKF v0.2) — Hybrid RAG Workbench")


@st.cache_resource(show_spinner="Indexing OKF bundle…")
def init_engine(bundle: str) -> OKFHybridRAGEngine:
    return OKFHybridRAGEngine(Path(bundle))


with st.sidebar:
    st.caption(f"Bundle: `{BUNDLE_PATH}`")
    if st.button("Reload bundle"):
        init_engine.clear()
    provider = ("Gemini" if os.getenv("GEMINI_API_KEY")
                else "OpenAI" if os.getenv("OPENAI_API_KEY") else "Offline (no API key)")
    st.caption(f"Synthesis: **{provider}**")

try:
    engine = init_engine(str(BUNDLE_PATH))
except Exception as exc:  # e.g. bundle missing, or embedding model download blocked
    st.error(f"Could not start the engine: {exc}")
    st.stop()
if engine.load_errors:
    st.warning("Some files could not be parsed and were skipped: "
               + ", ".join(f"`{p}`" for p in engine.load_errors))

tab_chat, tab_graph, tab_audit = st.tabs(
    ["Hybrid OKF + RAG assistant", "Concept graph", "Conformance & trust audit"])

with tab_chat:
    st.subheader("Ask across policies, runbooks and attested computations")
    col_q, col_opts = st.columns([3, 1])
    with col_q:
        query = st.text_area(
            "Question",
            value="How do I troubleshoot VPN drops when accessing production, "
                  "and which policies or SLA checks apply?",
            height=90,
        )
    with col_opts:
        top_k = st.slider("Semantic entry concepts (k)", 1, max(1, min(6, len(engine.concepts))), 2)
        hop_depth = st.slider("Link traversal hops", 0, 3, 1)

    if st.button("Run hybrid retrieval", type="primary", disabled=not query.strip()):
        retrieval = engine.retrieve_with_graph_expansion(query, top_k=top_k, hop_depth=hop_depth)
        left, right = st.columns([1.1, 1.4])
        with left:
            st.markdown("#### 1 · Semantic entry concepts (ChromaDB)")
            for sid in retrieval.seed_ids:
                c = engine.concepts[sid]
                dist = retrieval.seed_distances.get(sid)
                st.info(f"**{c.title}** (`{c.rel_path}`)  \n"
                        f"type `{c.concept_type}` · status `{c.status}` · trust `{c.trust_tier}`"
                        + (f" · distance `{dist:.3f}`" if dist is not None else ""))
            st.markdown("#### 2 · Graph expansion (NetworkX)")
            if retrieval.traversal_paths:
                for p in retrieval.traversal_paths:
                    st.success(f"`{p}`")
            else:
                st.caption("No additional concepts within the hop radius.")
            flagged = [c for c in retrieval.concepts if c.is_stale() or c.status == "deprecated"]
            if flagged:
                st.markdown("#### 3 · Trust gate")
                for c in flagged:
                    st.error(f"`{c.rel_path}` is "
                             + ("DEPRECATED" if c.status == "deprecated" else f"STALE ({c.stale_after})"))
        with right:
            st.markdown("#### Grounded answer")
            with st.spinner("Synthesising with OKF provenance…"):
                answer = engine.answer_query(query, retrieval)
            st.markdown(answer)
            with st.expander("Raw OKF context sent to the LLM"):
                st.code(engine.format_okf_context_prompt(retrieval.concepts), language="markdown")

with tab_graph:
    st.subheader("Bundle topology")
    st.write(f"**Concepts:** {len(engine.concepts)} · **Links:** {engine.graph.number_of_edges()}")
    dot = ["digraph OKF {", "rankdir=LR;", 'node [shape=box, style="rounded,filled", fillcolor="#eef3fb"];']
    for cid, c in engine.concepts.items():
        color = "#fde2e1" if (c.is_stale() or c.status == "deprecated") else "#eef3fb"
        label = f"{c.title}\\n({c.concept_type})".replace('"', "'")
        dot.append(f'"{cid}" [label="{label}", fillcolor="{color}"];')
    for u, v in engine.graph.edges():
        dot.append(f'"{u}" -> "{v}";')
    dot.append("}")
    st.graphviz_chart("\n".join(dot))
    st.table([{"From": u, "To": v} for u, v in engine.graph.edges()] or [{"From": "—", "To": "—"}])
    broken = [(c.rel_path, b) for c in engine.concepts.values() for b in c.broken_links]
    if broken:
        st.warning("Broken links (tolerated per §11, but worth fixing):")
        st.table([{"In": p, "Missing target": f"/{b}.md"} for p, b in broken])

with tab_audit:
    st.subheader("OKF v0.2 conformance report")
    results = validate_okf_bundle(BUNDLE_PATH)
    n_err = sum(len(r.errors) for r in results)
    n_warn = sum(len(r.warnings) for r in results)
    st.write(f"**{len(results)} files · {n_err} errors · {n_warn} warnings**")
    for r in results:
        badge = "✅ PASS" if r.valid else "❌ FAIL"
        kind = r.metadata.get("type", "reserved") if r.kind == "concept" else "reserved"
        with st.expander(f"{badge} — `{r.path}` (type: `{kind}`)"):
            if r.metadata:
                # YAML dates parse to datetime.date; stringify for JSON display
                st.json(json.loads(json.dumps(r.metadata, default=str)), expanded=False)
            for e in r.errors:
                st.error(e)
            for w in r.warnings:
                st.warning(w)
