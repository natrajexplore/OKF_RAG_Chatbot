# CLAUDE.md — OKF v0.2 Hybrid RAG Engine

## Project overview
Hybrid RAG application built on Google Cloud's **Open Knowledge Format (OKF) v0.2**
(released 2026-07-24, spec: `GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`).

Retrieval runs in three stages:
1. **Semantic entry discovery** — ChromaDB finds the top-k concepts (each OKF concept is one
   whole document; we never chunk across concept boundaries).
2. **Deterministic graph expansion** — NetworkX follows explicit Markdown links between
   concepts (outbound and inbound, up to N hops).
3. **Trust & freshness gate** — OKF v0.2 `status`, `stale_after`, `verified` are rendered
   into the LLM context so the answer cites provenance and warns about stale/deprecated
   knowledge.

## Layout
```
okf_bundle/          OKF v0.2 knowledge bundle (the source of truth)
src/okf_spec.py      Spec constants + helpers (actors, staleness, trust tier, links)
src/embeddings.py    Embedding selection (Ollama local, OKF_EMBEDDING=hash offline, or Chroma default)
src/validator.py     Producer-side lint: §11 conformance + v0.2 trust/lifecycle checks
src/parser.py        Concept loader + NetworkX link graph
src/engine.py        ChromaDB + graph-expansion retriever; Ollama/Gemini/OpenAI synthesis
src/demo_lab.py      Secure-request demo sandbox (insecure vs secured per OWASP weakness)
src/api.py           FastAPI backend (/api/chat, /api/graph, /api/demo/*) + serves src/static/
src/static/          Cisco-style web UI (hero, assistant, demo lab, graph, chatbot widget)
src/app.py           Streamlit UI (chat / graph / audit tabs)
tests/               pytest suite (no network or API keys needed)
```

The `okf_bundle/` also carries a defensive **API-security knowledge base** (from *Hacking APIs*
+ OWASP API Top 10): `api_security/`, `vulnerabilities/`, `controls/`, `runbooks/api_testing/`,
`standards/`. Default LLM + embeddings are **local Ollama** (no API keys); model names come
from env vars (`OLLAMA_MODEL`, `OLLAMA_EMBED_MODEL`).

## OKF v0.2 rules — enforce when editing `okf_bundle/`
1. **Frontmatter (§11):** every non-reserved `.md` file starts with a YAML block delimited by `---`.
2. **`type` is the ONLY required key (§4.1):** non-empty string. Type values are not centrally
   registered — use descriptive strings (`policy`, `runbook`, …).
3. **Reserved files (§3.1):** `index.md` and `log.md` are never concepts. Only the **root**
   `index.md` may carry frontmatter, and only `okf_version: "0.2"`. `log.md` uses ISO
   `## YYYY-MM-DD` headings, newest first.
4. **Identity & links (§2, §6.1):** concept ID = bundle-relative path minus `.md`
   (`/policies/remote_access.md` → `policies/remote_access`). Prefer bundle-absolute links:
   `[Zero Trust VPN Runbook](/runbooks/zero_trust_vpn.md)`.
5. **Provenance (§5.1):** `sources:` is a list; each entry REQUIRES `resource`; optional `id`,
   `title`, `author`, `last_modified`. Footnotes `[^id]` join to `sources[].id`.
6. **Trust (§5.2, §7):** `generated: {by, at}`, `verified: [{by, at}]` (a bare mapping is a
   one-element list). Actors: `human:<id>` | `process:<id>` | `<producer>/<version>`.
7. **Lifecycle (§5.5):** `status: draft | stable | deprecated` — **absent means `stable`**.
   `stale_after: YYYY-MM-DD` — a concept is stale when **today >= stale_after**.
8. **Attested Computation (§10.2):** `type: Attested Computation` (exact string), `runtime`
   REQUIRED; optional `parameters`, `computation`, `executor`, `attester`. If `computation`
   is absent, the body carries a `# Computation` heading with a fenced block.
9. **Consumers MUST NOT reject (§11)** unknown types, unknown keys, broken links, or missing
   optional fields. The parser/engine tolerate all of these; the validator only *warns*.

## Commands (uv + Python 3.12)
- Install: `uv sync`
- Validate bundle: `uv run python -m src.validator` (add `--strict` to fail on warnings)
- Tests: `uv run pytest -q`
- Run web app (FastAPI + chatbot + demo): `uv run uvicorn src.api:app` → http://127.0.0.1:8000
- Run Streamlit workbench: `uv run streamlit run src/app.py`

## Conventions
- After any change under `okf_bundle/`, run the validator; it must report 0 errors.
- Add a dated entry to `okf_bundle/log.md` for every bundle change (newest first).
- Keep secrets in `.env` (never commit). Model names come from env vars, not code.
- Tests must not need network access or API keys (inject the embedding function).
