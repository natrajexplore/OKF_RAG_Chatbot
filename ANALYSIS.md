# Review of the Gemini blueprint ("OKF v0.2 Hybrid RAG Engine")

Gemini's architecture is sound — whole-concept indexing, vector entry points, link-graph
expansion and a trust/freshness gate is the right shape for OKF. The files, however, would not
run as written and diverge from the OKF v0.2 spec in several places. Everything below is fixed
in this project and covered by tests. Spec references are to OKF v0.2 SPEC.md
(GoogleCloudPlatform/knowledge-catalog, released 2026-07-24).

## Blocking bugs (the app would not start or files would be corrupt)

| # | Problem in Gemini's version | Fix |
|---|---|---|
| 1 | `streamlit run src/app.py` puts `src/` on `sys.path`, so `from src.validator import …` raises `ModuleNotFoundError: No module named 'src'`. | `app.py` adds the project root to `sys.path` before importing. |
| 2 | The SQL code fence in `computations/sla_uptime_check.md` is never closed; copying the response verbatim pastes `validator.py` and everything after it into that Markdown file. | Fence closed; file verified by the validator. |
| 3 | `.env.example` is listed in the tree but never provided. | Added, with model and embedding settings. |
| 4 | Validator always exits 0, so it can't gate CI or Claude Code. | Exit 1 on errors; `--strict` also fails on warnings. |

## Spec conformance errors

| # | Gemini | OKF v0.2 | Fix |
|---|---|---|---|
| 5 | `type: attested_computation` | Exact type string is `Attested Computation` (§10.2). With Gemini's value, OKF-aware consumers treat it as an ordinary concept and ignore `runtime`/`executor`/`attester`. | Corrected; validator warns on look-alike spellings. |
| 6 | `sources: [{uri, description}]` | Each entry REQUIRES `resource`; optional `id`, `title`, `author`, `last_modified`; footnotes `[^id]` join to `sources[].id` (§5.1). | Corrected; validator checks `resource` and footnote joins. |
| 7 | Stale when `stale_after < today` | Stale when `today >= stale_after` (§5.5). Off by one day. | Fixed in one shared helper. |
| 8 | Validator defaults missing `status` to `draft`; parser defaults to `stable`. | Absent status means `stable` (§5.5). | Single default used everywhere. |
| 9 | Parser iterates `verified` as a list; a bare mapping `verified: {by, at}` loses the attestation. | A bare mapping MUST be treated as a one-element list (§5.2). | Normalised in one helper. |
| 10 | Reserved files only skipped; nested `index.md`/`log.md` with frontmatter pass silently; no `log.md`. | Only the root `index.md` may carry frontmatter (`okf_version` only); `log.md` uses ISO dates, newest first (§3.1, §8, §9). | Enforced; sample `log.md` added. |
| 11 | CLAUDE.md tells Claude to use `agent/<model>` actors. | Actor convention is `human:<id>` / `process:<id>` / `<producer>/<version>` (§7). | CLAUDE.md and sample files corrected; validator checks actors. |
| 12 | One unparseable file crashes the parser and the whole app. | Consumers must not reject a bundle over unknown types/keys, broken links or missing optional fields (§11). | Bad files are skipped and reported; broken links recorded, not dropped. |

## Retrieval and robustness issues

| # | Problem | Fix |
|---|---|---|
| 13 | `chromadb.Client()` + a fixed collection name: every engine in the process shares one collection, so Streamlit reruns and tests see stale documents. | Unique ephemeral collection per engine; optional `CHROMA_PATH` persistence that deletes concepts removed from the bundle. |
| 14 | 2-hop neighbours are added but no traversal path is recorded for them, so the UI can't explain why they were retrieved. | Shortest path recorded for every expanded concept, with link direction (`->` / `<-`). |
| 15 | Link regex misses `/a.md#section`, matches image links, and turns links inside code fences into graph edges. | Regex handles fragments and images; fenced code is stripped before extraction; links escaping the bundle root are ignored. |
| 16 | Empty bundle or empty query → `n_results=0` exception. | Guarded. |
| 17 | System prompt concatenated into Gemini `contents`; model names hard-coded; any provider error crashes the page. | `system_instruction` + temperature via `GenerateContentConfig`; models from env; provider errors fall back to an offline summary with the error shown. |
| 18 | Chroma's default embedder downloads a model on first use; when blocked, the app dies with a raw proxy/HTTP error. | Clear error explaining the cause, plus `OKF_EMBEDDING=hash` offline embedder. |

## Added beyond the blueprint

- `src/okf_spec.py` — one place for spec constants and helpers, so validator, parser and engine can't drift apart again (items 7–9 were exactly that drift).
- 19 pytest tests that run offline, including spec edge cases (stale boundary, bare `verified`, link resolution).
- GitHub Actions workflow (one of Gemini's own suggested follow-ups).
- Graph visualisation tab and a trust-gate panel that flags stale/deprecated concepts in the result.

## Verified in this build

- `python -m src.validator` → 6 files, 0 errors, 0 warnings.
- `pytest` → 19 passed (chromadb 1.5.9, networkx 3.7, streamlit 1.66.1, Python 3.13).
- Streamlit app exercised headlessly: chat retrieval, graph and audit tabs render with no exceptions.
- Not exercised here: live Gemini/OpenAI calls (no keys in this environment) and Chroma's
  default model download (network blocked in this environment). Both paths are standard
  library usage; run `uv run streamlit run src/app.py` once with a key to confirm.
