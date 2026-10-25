"""Hybrid OKF retriever: ChromaDB semantic entry points + NetworkX link expansion,
with OKF v0.2 trust/freshness rendered into the LLM context."""

from __future__ import annotations

import datetime as dt
import json
import os
import urllib.request
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import chromadb
import networkx as nx
from dotenv import load_dotenv

from src.embeddings import embedding_from_env, ollama_base_url
from src.parser import OKFConcept, load_okf_bundle

load_dotenv()

SYSTEM_PROMPT = (
    "You are an enterprise OKF v0.2 knowledge agent. Answer strictly from the OKF concepts "
    "provided. Always:\n"
    "1. Cite the exact concept path in brackets, e.g. [/policies/remote_access.md].\n"
    "2. State the trust tier and freshness of every concept you rely on.\n"
    "3. If a concept is STALE or DEPRECATED, warn the user prominently before using it.\n"
    "4. Explain how linked concepts connect (e.g. Policy -> Runbook -> Attested Computation).\n"
    "5. If the concepts do not answer the question, say so instead of guessing."
)


@dataclass
class RetrievalResult:
    query: str
    seed_ids: list[str]
    seed_distances: dict[str, float]
    expanded_ids: list[str]
    traversal_paths: list[str]
    concepts: list[OKFConcept] = field(default_factory=list)


class OKFHybridRAGEngine:
    def __init__(self, bundle_dir: Path, embedding_function: Any = None,
                 chroma_path: str | None = None, collection_name: str | None = None):
        self.bundle_dir = Path(bundle_dir)
        bundle = load_okf_bundle(self.bundle_dir)
        self.concepts = bundle.concepts
        self.graph = bundle.graph
        self.load_errors = bundle.load_errors
        self._undirected = self.graph.to_undirected(as_view=True)

        chroma_path = chroma_path if chroma_path is not None else os.getenv("CHROMA_PATH")
        if chroma_path:
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            name = collection_name or "okf_v02_concepts"
        else:
            # EphemeralClient state is shared per process; a unique name keeps
            # separate engine instances (tests, Streamlit reruns) isolated.
            self.chroma_client = chromadb.EphemeralClient()
            name = collection_name or f"okf_v02_{uuid.uuid4().hex[:8]}"

        if embedding_function is None:
            embedding_function = embedding_from_env()
        kwargs: dict[str, Any] = {"name": name, "metadata": {"hnsw:space": "cosine"}}
        if embedding_function is not None:
            kwargs["embedding_function"] = embedding_function
        self.collection = self.chroma_client.get_or_create_collection(**kwargs)
        try:
            self._index_concepts()
        except Exception as exc:
            if embedding_function is None:
                raise RuntimeError(
                    "Indexing failed while using Chroma's default embedding model, which is "
                    "downloaded on first use. Check network/proxy access, or set "
                    "OKF_EMBEDDING=hash in .env to use the offline embedder. "
                    f"Original error: {type(exc).__name__}: {exc}"
                ) from exc
            raise

    # ------------------------------------------------------------------ indexing
    def _index_concepts(self) -> None:
        current_ids = set(self.concepts)
        existing = set(self.collection.get(include=[])["ids"])
        stale = sorted(existing - current_ids)
        if stale:  # concepts removed from the bundle since the last persistent index
            self.collection.delete(ids=stale)
        if not self.concepts:
            return

        ids, docs, metas = [], [], []
        for cid, c in self.concepts.items():
            ids.append(cid)
            docs.append(f"Title: {c.title}\nType: {c.concept_type}\n"
                        f"Description: {c.description}\n\n{c.body}")
            metas.append({  # Chroma metadata values must be str/int/float/bool
                "concept_id": cid,
                "title": c.title,
                "type": c.concept_type,
                "status": c.status,
                "stale_after": c.stale_after or "none",
                "trust_tier": c.trust_tier,
                "verified_by": ",".join(c.verified_by) or "unverified",
            })
        self.collection.upsert(ids=ids, documents=docs, metadatas=metas)

    # ----------------------------------------------------------------- retrieval
    def _describe_path(self, path: list[str]) -> str:
        parts = [path[0]]
        for a, b in zip(path, path[1:]):
            arrow = "->" if self.graph.has_edge(a, b) else "<-"
            parts.append(f" {arrow} {b}")
        return "".join(parts)

    def retrieve_with_graph_expansion(self, query: str, top_k: int = 2,
                                      hop_depth: int = 1) -> RetrievalResult:
        """Stage 1: semantic entry points. Stage 2: follow OKF links (both directions)."""
        n = min(max(top_k, 1), len(self.concepts))
        if n == 0 or not query.strip():
            return RetrievalResult(query, [], {}, [], [], [])

        res = self.collection.query(query_texts=[query], n_results=n,
                                    include=["distances"])
        seed_ids = [i for i in (res.get("ids") or [[]])[0] if i in self.concepts]
        dists = (res.get("distances") or [[]])[0]
        seed_distances = {cid: float(d) for cid, d in zip(seed_ids, dists)}

        best_path: dict[str, list[str]] = {}
        for seed in seed_ids:
            if seed not in self._undirected or hop_depth < 1:
                continue
            paths = nx.single_source_shortest_path(self._undirected, seed, cutoff=hop_depth)
            for node, path in paths.items():
                if node in seed_ids:
                    continue
                if node not in best_path or len(path) < len(best_path[node]):
                    best_path[node] = path

        expanded_ids = sorted(best_path, key=lambda cid: (len(best_path[cid]), cid))
        traversal_paths = [self._describe_path(best_path[cid]) for cid in expanded_ids]
        ordered = seed_ids + expanded_ids
        return RetrievalResult(
            query=query,
            seed_ids=seed_ids,
            seed_distances=seed_distances,
            expanded_ids=expanded_ids,
            traversal_paths=traversal_paths,
            concepts=[self.concepts[cid] for cid in ordered],
        )

    # ----------------------------------------------------------------- synthesis
    @staticmethod
    def format_okf_context_prompt(concepts: list[OKFConcept],
                                  today: dt.date | None = None) -> str:
        today = today or dt.date.today()
        blocks = []
        for c in concepts:
            if c.stale_after is None:
                freshness = "NO EXPIRY DECLARED"
            elif c.is_stale(today):
                freshness = f"STALE (stale_after {c.stale_after})"
            else:
                freshness = f"FRESH (valid until {c.stale_after})"
            trust = (f"{c.trust_tier.upper()} by [{', '.join(c.verified_by)}]"
                     if c.verified_by else "UNVERIFIED")
            status = c.status.upper() if c.status == "deprecated" else c.status
            blocks.append(
                f"--- START OKF CONCEPT [{c.rel_path}] ---\n"
                f"ID: {c.concept_id} | Type: {c.concept_type} | Status: {status}\n"
                f"Trust: {trust} | Freshness: {freshness}\n"
                f"Links to: {', '.join(c.outbound_links) or 'none'}\n\n"
                f"{c.body.strip()}\n"
                f"--- END OKF CONCEPT [{c.rel_path}] ---"
            )
        return "\n\n".join(blocks)

    def _offline_answer(self, retrieval: RetrievalResult, note: str) -> str:
        lines = [f"**[Offline synthesis — {note}]**", "",
                 f"Retrieved **{len(retrieval.concepts)}** OKF concepts:"]
        for c in retrieval.concepts:
            flags = []
            if c.status == "deprecated":
                flags.append("DEPRECATED")
            if c.is_stale():
                flags.append("STALE")
            flag_txt = f" ⚠ {' / '.join(flags)}" if flags else ""
            lines.append(f"- `[{c.rel_path}]` ({c.concept_type}, {c.trust_tier}){flag_txt} — "
                         f"{c.description or c.title}")
        if retrieval.traversal_paths:
            lines += ["", "**Graph traversal:**"] + [f"- `{p}`" for p in retrieval.traversal_paths]
        return "\n".join(lines)

    @staticmethod
    def _answer_ollama(system_prompt: str, user_message: str) -> str:
        """Local Ollama chat (no API key). Model/host from env vars."""
        host = ollama_base_url()
        model = os.getenv("OLLAMA_MODEL", "nemotron-3-nano:4b")
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_message}],
            "stream": False,
            "think": False,           # suppress thinking traces on reasoning models
            "options": {"temperature": 0.1},
        }).encode()
        req = urllib.request.Request(
            f"{host}/api/chat", data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=float(os.getenv("OLLAMA_TIMEOUT", "300"))) as resp:
            data = json.loads(resp.read())
        return (data.get("message") or {}).get("content", "") or ""

    def answer_query(self, query: str, retrieval: RetrievalResult) -> str:
        if not retrieval.concepts:
            return "No OKF concepts matched this question."
        # Cap the full-text context sent to the LLM so local CPU inference stays responsive;
        # retrieval.concepts (and the API's citations) still expose every retrieved concept.
        max_ctx = max(1, int(os.getenv("OKF_MAX_CONTEXT", "3")))
        context = self.format_okf_context_prompt(retrieval.concepts[:max_ctx])
        user_message = f"OKF knowledge context:\n{context}\n\nUser question: {query}"

        try:
            # Local-first: Ollama needs no API key and keeps data on the machine.
            if os.getenv("OLLAMA_MODEL") or os.getenv("OKF_LLM", "").lower() == "ollama":
                return self._answer_ollama(SYSTEM_PROMPT, user_message)

            if os.getenv("GEMINI_API_KEY"):
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
                resp = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                    contents=user_message,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT,
                                                       temperature=0.1),
                )
                return resp.text or ""

            if os.getenv("OPENAI_API_KEY"):
                from openai import OpenAI

                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
                resp = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "system", "content": SYSTEM_PROMPT},
                              {"role": "user", "content": user_message}],
                    temperature=0.1,
                )
                return resp.choices[0].message.content or ""
        except Exception as exc:  # surface provider errors without losing retrieval
            return self._offline_answer(retrieval, f"LLM call failed: {type(exc).__name__}: {exc}")

        return self._offline_answer(retrieval, "set OLLAMA_MODEL (local, no key) or "
                                               "GEMINI_API_KEY / OPENAI_API_KEY in .env "
                                               "for LLM generation")
