"""Shared fixtures. Tests never touch the network: Chroma gets the deterministic
hashing embedder instead of downloading its default ONNX model."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from src.embeddings import HashingEmbedding

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_BUNDLE = PROJECT_ROOT / "okf_bundle"


@pytest.fixture
def embedding_fn() -> HashingEmbedding:
    return HashingEmbedding()


@pytest.fixture
def sample_bundle() -> Path:
    return SAMPLE_BUNDLE


@pytest.fixture
def make_bundle(tmp_path: Path):
    """make_bundle({"policies/a.md": "...", ...}) -> bundle dir with dedented files."""

    def _make(files: dict[str, str]) -> Path:
        root = tmp_path / "bundle"
        for rel, content in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
        return root

    return _make
