"""Embedding function selection.

Default: Chroma's built-in all-MiniLM-L6-v2 (ONNX, downloaded once on first use, ~80 MB).
Offline: set OKF_EMBEDDING=hash for a deterministic, dependency-free feature-hashing
embedder. Retrieval quality is lower (lexical, not semantic) but it needs no network,
which suits air-gapped demos and CI.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import urllib.request

from chromadb import Documents, EmbeddingFunction, Embeddings


class HashingEmbedding(EmbeddingFunction):
    """Bag-of-words feature hashing -> L2-normalised vectors."""

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim

    def __call__(self, input: Documents) -> Embeddings:  # noqa: A002 (chroma's signature)
        vectors = []
        for text in input:
            vec = [0.0] * self.dim
            for tok in re.findall(r"[a-z0-9]+", text.lower()):
                vec[int(hashlib.md5(tok.encode()).hexdigest(), 16) % self.dim] += 1.0
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vectors.append([v / norm for v in vec])
        return vectors

    @staticmethod
    def name() -> str:
        return "okf-hashing"

    def get_config(self) -> dict:
        return {"dim": self.dim}

    @staticmethod
    def build_from_config(config: dict) -> "HashingEmbedding":
        return HashingEmbedding(dim=int(config.get("dim", 512)))


def ollama_base_url(host: str | None = None) -> str:
    """Resolve a usable Ollama client URL.

    Accepts a full URL, a bare host, or a host:port. Note that a common system setting is
    `OLLAMA_HOST=0.0.0.0`, which is the *server* bind address, not a client URL — map it to
    127.0.0.1 and add the scheme/port so the client can actually connect.
    """
    raw = (host or os.getenv("OLLAMA_URL") or os.getenv("OLLAMA_HOST")
           or "http://localhost:11434").strip().rstrip("/")
    if not raw:
        raw = "http://localhost:11434"
    if "://" not in raw:
        raw = "http://" + raw
    scheme, _, rest = raw.partition("://")
    rest = rest or "localhost"
    hostpart, colon, port = rest.partition(":")
    if hostpart in ("0.0.0.0", "::", ""):
        hostpart = "127.0.0.1"
    if not colon:
        port = "11434"
    return f"{scheme}://{hostpart}:{port}"


class OllamaEmbedding(EmbeddingFunction):
    """Embeddings from a local Ollama server (no API key, fully offline).

    Uses the /api/embed batch endpoint. Model and host come from env vars so nothing is
    hard-coded (OKF v0.2 convention).
    """

    def __init__(self, model: str | None = None, host: str | None = None,
                 timeout: float = 120.0) -> None:
        self.model = model or os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.host = ollama_base_url(host)
        self.timeout = timeout

    def __call__(self, input: Documents) -> Embeddings:  # noqa: A002 (chroma's signature)
        payload = json.dumps({"model": self.model, "input": list(input)}).encode()
        req = urllib.request.Request(
            f"{self.host}/api/embed", data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
        embeddings = data.get("embeddings")
        if not embeddings:
            raise RuntimeError(f"Ollama returned no embeddings for model {self.model!r}")
        return [[float(x) for x in vec] for vec in embeddings]

    @staticmethod
    def name() -> str:
        return "okf-ollama"

    def get_config(self) -> dict:
        return {"model": self.model, "host": self.host}

    @staticmethod
    def build_from_config(config: dict) -> "OllamaEmbedding":
        return OllamaEmbedding(model=config.get("model"), host=config.get("host"))


def embedding_from_env():
    """Return an embedding function per OKF_EMBEDDING, or None for Chroma's default.

    "hash"   -> offline lexical embedder (no network)
    "ollama" -> local Ollama server (nomic-embed-text by default)
    other    -> None (Chroma's bundled all-MiniLM, downloaded on first use)
    """
    choice = os.getenv("OKF_EMBEDDING", "default").strip().lower()
    if choice == "hash":
        return HashingEmbedding()
    if choice == "ollama":
        return OllamaEmbedding()
    return None
