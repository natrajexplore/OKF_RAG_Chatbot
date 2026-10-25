# OKF RAG Engine

Hybrid Retrieval-Augmented Generation over a Google Cloud **Open Knowledge Format (OKF) v0.2**
bundle: semantic entry points from ChromaDB, deterministic expansion along explicit Markdown
links with NetworkX, and answers that cite each concept's trust tier and freshness.

```
question ──► ChromaDB (top-k whole concepts) ──► NetworkX link expansion (N hops, both directions)
                                                         │
             answer with [/path.md] citations ◄── LLM ◄──┴── context annotated with status,
             + STALE / DEPRECATED warnings                    stale_after, verified (trust tier)
```

## Two front ends

- **`src/api.py`** — a FastAPI web app: a **Cisco-style** site with an **API-security chatbot**
  and a **secure-request demo lab** (each OWASP weakness shown insecure vs. secured on an
  in-memory sandbox). Answers are generated **locally by Ollama** — no API keys.
- **`src/app.py`** — the original Streamlit workbench (chat / graph / conformance audit).

## Quick start (local, no API keys)

```bash
uv sync
cp .env.example .env          # defaults to local Ollama; no keys needed

# one-time: pull the local models used by default
ollama pull nemotron-3-nano:4b   # chat generation
ollama pull nomic-embed-text     # embeddings

uv run python -m src.validator   # 41 files, 0 errors
uv run pytest -q                 # 28 offline tests

uv run uvicorn src.api:app       # web UI + chatbot + demo  → http://127.0.0.1:8000
uv run streamlit run src/app.py  # (optional) Streamlit workbench
```

The default `.env` runs **fully local via Ollama**. The model and embedder come from env
vars, so you can point `OLLAMA_MODEL` at any installed model. With no LLM configured at all,
retrieval + graph traversal still work and synthesis returns a structured offline summary;
set `OKF_EMBEDDING=hash` to skip the embedding server entirely. Frontier providers
(`GEMINI_API_KEY` / `OPENAI_API_KEY`) remain supported but are optional.

> **Note on the UI:** the web front end mimics the *look and feel* of cisco.com for the demo
> experience only. It uses an original "Sentinel" brand and is **not affiliated with, or
> endorsed by, Cisco Systems, Inc.**

## API-security knowledge base

`okf_bundle/` now also holds a **defensive API-security knowledge base** summarised from
*Hacking APIs* (Corey J. Ball, No Starch Press) and the OWASP API Security Top 10:
a hub, an API security policy, OWASP 2019/2023 standards, **13 weakness concepts**
(`vulnerabilities/`), **8 controls** (`controls/`) and **10 assurance checklists**
(`runbooks/api_testing/`) — all OKF v0.2 concepts with sources, links and a trust gate.

## What's in the box

| Path | Purpose |
|---|---|
| `okf_bundle/` | Enterprise-ops samples **+ API-security knowledge base** (39 concepts, root `index.md`, `log.md`) |
| `src/validator.py` | §11 conformance errors + v0.2 trust/lifecycle/provenance/link warnings; `--strict` for CI |
| `src/parser.py` | Tolerant consumer: loads concepts, builds the link graph, records broken links |
| `src/embeddings.py` | Embedding selection: Ollama (local), hashing (offline), or Chroma default |
| `src/engine.py` | Hybrid retriever + **Ollama** / Gemini / OpenAI synthesis with provenance-first prompt |
| `src/demo_lab.py` | Secure-request demo sandbox: insecure vs. secured handling of each OWASP weakness |
| `src/api.py` | FastAPI backend: `/api/chat`, `/api/graph`, `/api/demo/*`, serves the web UI |
| `src/static/` | Cisco-style single-page UI: hero, assistant, demo console, graph, chatbot widget |
| `src/app.py` | Streamlit: chat, concept-graph view, conformance audit |
| `tests/` | 28 offline tests (no network, no keys) |
| `.github/workflows/okf-validate.yml` | Validate + test on every PR |
| `CLAUDE.md` | OKF v0.2 rules and commands for Claude Code |

## Using your own knowledge

Replace or extend `okf_bundle/`. Each concept is one Markdown file whose only required
frontmatter key is `type`; add `title`, `description`, `status`, `stale_after`, `sources`,
`generated` and `verified` to get trust and freshness signals in answers. Link concepts with
bundle-absolute links such as `[VPN runbook](/runbooks/zero_trust_vpn.md)`. Run the validator
after every change and add an entry to `log.md`.

## Working with Claude Code

Open the folder and run `claude`. `CLAUDE.md` gives it the OKF v0.2 rules, so prompts like
"convert `docs/firewall-standard.pdf` into OKF concepts and link them to the remote access
policy, then run the validator" work without re-explaining the format.
