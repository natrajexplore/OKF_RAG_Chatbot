"""FastAPI backend for the OKF API-Security assistant.

Serves the single-page frontend (static/) and three groups of endpoints:
  /api/chat      hybrid RAG Q&A over the OKF bundle, answered locally by Ollama
  /api/graph     concept graph for the UI
  /api/demo/*    the secure-request demo lab (vulnerable vs secure, in-memory sandbox)

Run from the project root:  uv run uvicorn src.api:app --reload
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv  # noqa: E402

from src import demo_lab  # noqa: E402
from src.embeddings import HashingEmbedding, embedding_from_env  # noqa: E402
from src.engine import OKFHybridRAGEngine  # noqa: E402

load_dotenv()

BUNDLE_PATH = Path(os.getenv("OKF_BUNDLE_PATH", PROJECT_ROOT / "okf_bundle"))
STATIC_DIR = Path(__file__).resolve().parent / "static"

_engine: OKFHybridRAGEngine | None = None
_engine_note = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_engine()  # build (and index) the bundle once at startup
    yield


app = FastAPI(title="OKF API-Security Assistant", version="0.2.1", lifespan=lifespan)


def get_engine() -> OKFHybridRAGEngine:
    """Build the engine once. If the configured embedder is unreachable (e.g. Ollama is
    down), fall back to the offline hashing embedder so the demo still runs."""
    global _engine, _engine_note
    if _engine is not None:
        return _engine
    try:
        _engine = OKFHybridRAGEngine(BUNDLE_PATH, embedding_function=embedding_from_env())
        _engine_note = f"embedding: {os.getenv('OKF_EMBEDDING', 'default')}"
    except Exception as exc:  # embedder/network problem — degrade gracefully
        _engine = OKFHybridRAGEngine(BUNDLE_PATH, embedding_function=HashingEmbedding())
        _engine_note = f"fell back to offline hashing embedder ({type(exc).__name__})"
    return _engine


# ------------------------------------------------------------------ chat / graph
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=6)
    hop_depth: int = Field(1, ge=0, le=3)


@app.post("/api/chat")
def chat(body: ChatRequest) -> dict:
    engine = get_engine()
    r = engine.retrieve_with_graph_expansion(body.query, top_k=body.top_k,
                                              hop_depth=body.hop_depth)
    answer = engine.answer_query(body.query, r)
    citations = []
    for c in r.concepts:
        citations.append({
            "concept_id": c.concept_id, "path": c.rel_path, "title": c.title,
            "type": c.concept_type, "status": c.status, "trust_tier": c.trust_tier,
            "stale": c.is_stale(), "stale_after": c.stale_after,
            "seed": c.concept_id in r.seed_ids,
        })
    flagged = [{"path": c.rel_path,
                "reason": "DEPRECATED" if c.status == "deprecated"
                else f"STALE (stale_after {c.stale_after})"}
               for c in r.concepts if c.is_stale() or c.status == "deprecated"]
    return {"answer": answer, "citations": citations,
            "traversal": r.traversal_paths, "trust_flags": flagged,
            "seed_ids": r.seed_ids, "expanded_ids": r.expanded_ids}


@app.get("/api/graph")
def graph() -> dict:
    engine = get_engine()
    nodes = [{"id": cid, "title": c.title, "type": c.concept_type,
              "status": c.status, "stale": c.is_stale(), "trust": c.trust_tier}
             for cid, c in engine.concepts.items()]
    edges = [{"source": u, "target": v} for u, v in engine.graph.edges()]
    return {"nodes": nodes, "edges": edges, "count": len(nodes),
            "link_count": len(edges), "note": _engine_note}


@app.get("/api/health")
def health() -> dict:
    engine = get_engine()
    provider = ("ollama" if os.getenv("OLLAMA_MODEL") or os.getenv("OKF_LLM", "").lower() == "ollama"
                else "gemini" if os.getenv("GEMINI_API_KEY")
                else "openai" if os.getenv("OPENAI_API_KEY") else "offline")
    return {"status": "ok", "concepts": len(engine.concepts), "provider": provider,
            "ollama_model": os.getenv("OLLAMA_MODEL", "nemotron-3-nano:4b"),
            "engine_note": _engine_note}


# ------------------------------------------------------------------ demo lab
@app.get("/api/demo/scenarios")
def demo_scenarios() -> dict:
    return {"scenarios": demo_lab.SCENARIOS}


class DemoRequest(BaseModel):
    mode: str = Field("vulnerable", pattern="^(vulnerable|secure)$")
    params: dict = Field(default_factory=dict)


@app.post("/api/demo/{scenario}")
def demo(scenario: str, body: DemoRequest) -> dict:
    mode, p = body.mode, body.params
    try:
        if scenario == "bola":
            return demo_lab.bola(mode, p.get("caller", "alice"), int(p.get("account_id", 5502)))
        if scenario == "auth":
            if p.get("reset"):
                demo_lab.reset_login_state()
            return demo_lab.login(mode, p.get("username", "alice"),
                                  p.get("password", "wrong-guess"))
        if scenario == "jwt":
            token = p.get("token") or _forged_none_token()
            return demo_lab.verify_jwt(mode, token)
        if scenario == "mass":
            return demo_lab.register(mode, p.get("body") or
                                     {"username": "mallory", "password": "x", "isAdmin": True})
        if scenario == "injection":
            return demo_lab.search(mode, p.get("name", "' OR '1'='1"))
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=f"Bad demo parameters: {exc}") from exc
    raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario}")


@app.get("/api/demo/jwt/sample")
def jwt_sample() -> dict:
    """Give the UI a valid admin token and a forged 'none' token to try."""
    return {"valid_admin": demo_lab.issue_jwt("alice", "admin"),
            "forged_none": _forged_none_token()}


def _forged_none_token() -> str:
    import base64 as _b64
    import json as _json

    def seg(obj):
        return _b64.urlsafe_b64encode(_json.dumps(obj).encode()).rstrip(b"=").decode()
    # alg:none, admin role, empty signature — the classic forged token
    return f"{seg({'alg': 'none', 'typ': 'JWT'})}.{seg({'sub': 'mallory', 'role': 'admin'})}."


# ------------------------------------------------------------------ static site
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")
