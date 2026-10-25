"""OKF v0.2 spec constants and small, dependency-free helpers shared by the
validator, parser and engine. Section numbers refer to the OKF v0.2 SPEC.md."""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import PurePosixPath
from typing import Any

OKF_VERSION = "0.2"
RESERVED_FILES = frozenset({"index.md", "log.md"})          # §3.1
REQUIRED_KEYS = ("type",)                                   # §4.1 — the only required key
ATTESTED_COMPUTATION_TYPE = "Attested Computation"          # §10.2 — exact type string
VALID_STATUSES = frozenset({"draft", "stable", "deprecated"})  # §5.5
DEFAULT_STATUS = "stable"                                   # §5.5 — absent status means stable

# §7 actor convention: human:<id> | process:<id> | <producer>/<version>
ACTOR_PATTERN = re.compile(r"^(human:|process:|[\w.-]+/).+$")
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Markdown inline links ending in .md, optionally with a #fragment, ignoring images.
FENCED_BLOCK_PATTERN = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.MULTILINE | re.DOTALL)
COMPUTATION_HEADING_PATTERN = re.compile(r"^#\s+Computation\s*$", re.MULTILINE)
MD_LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]*)\]\(\s*<?([^)\s>]+?\.md)(#[^)\s>]*)?>?(?:\s+\"[^\"]*\")?\s*\)")


def to_iso_date(value: Any) -> str | None:
    """Normalise a YAML date/datetime/string to YYYY-MM-DD, or None if unusable."""
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.date().isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    text = str(value).strip()
    if ISO_DATE_PATTERN.match(text[:10]):
        return text[:10]
    return None


def is_stale(stale_after: Any, today: _dt.date | None = None) -> bool:
    """§5.5: a concept is stale when today >= stale_after."""
    iso = to_iso_date(stale_after)
    if iso is None:
        return False
    today_iso = (today or _dt.date.today()).isoformat()
    return today_iso >= iso


def normalize_actor_events(value: Any) -> list[dict[str, Any]]:
    """§5.2: `verified` may be a list or a bare mapping (treated as a one-element list)."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, dict)]
    return []


def trust_tier(verified: Any) -> str:
    """Derived trust tier: human-reviewed > machine-confirmed > unverified."""
    events = normalize_actor_events(verified)
    actors = [str(e.get("by", "")) for e in events]
    if any(a.startswith("human:") for a in actors):
        return "human-reviewed"
    return "machine-confirmed" if actors else "unverified"


def effective_status(meta: dict[str, Any]) -> str:
    status = meta.get("status")
    return str(status) if status else DEFAULT_STATUS


def concept_id_from_rel_path(rel_path: str) -> str:
    """§2: concept ID is the bundle-relative path without the .md extension."""
    clean = rel_path.lstrip("/")
    return clean[:-3] if clean.endswith(".md") else clean


def resolve_link(source_rel_path: str, target: str) -> str | None:
    """Resolve a bundle-absolute (/a/b.md) or relative (../c.md) link to a concept ID.
    Returns None for external URLs or links that escape the bundle root."""
    if "://" in target or target.startswith("mailto:"):
        return None
    if target.startswith("/"):
        parts = PurePosixPath(target.lstrip("/")).parts
    else:
        parent = PurePosixPath(source_rel_path.lstrip("/")).parent
        parts = (parent / target).parts
    stack: list[str] = []
    for part in parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not stack:
                return None
            stack.pop()
        else:
            stack.append(part)
    return concept_id_from_rel_path("/".join(stack)) if stack else None


def extract_links(source_rel_path: str, body: str) -> list[str]:
    """Ordered, de-duplicated concept IDs linked from a concept body."""
    seen: list[str] = []
    prose = FENCED_BLOCK_PATTERN.sub("", body)  # links inside code fences are not edges
    for _label, target, _frag in MD_LINK_PATTERN.findall(prose):
        cid = resolve_link(source_rel_path, target)
        if cid and cid not in seen:
            seen.append(cid)
    return seen
