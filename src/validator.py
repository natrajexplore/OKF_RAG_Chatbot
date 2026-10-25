"""OKF v0.2 producer-side validator.

ERRORS are §11 conformance failures (unparseable/missing frontmatter, missing `type`,
reserved-file structure) plus the Attested Computation `runtime` requirement (§10.2).
WARNINGS cover v0.2 trust, lifecycle and provenance hygiene. Per §11, a *consumer* must
not reject a bundle for warnings — this tool is for authors and CI.

Usage: python -m src.validator [BUNDLE_DIR] [--strict]
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter
import yaml

from src import okf_spec as spec

FOOTNOTE_REF_PATTERN = re.compile(r"\[\^([^\]]+)\](?!:)")
LOG_HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class OKFValidationResult:
    path: str
    kind: str  # "concept" | "reserved"
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.errors


def _load(md_file: Path) -> tuple[bool, dict[str, Any], str, str | None]:
    """Return (has_frontmatter_block, metadata, body, parse_error)."""
    raw = md_file.read_text(encoding="utf-8")
    has_block = raw.lstrip("﻿").startswith("---")
    try:
        post = frontmatter.loads(raw)
    except yaml.YAMLError as exc:
        return has_block, {}, raw, f"YAML parse error: {exc}"
    except Exception as exc:  # frontmatter raises varied errors for non-mapping YAML
        return has_block, {}, raw, f"frontmatter parse error: {exc}"
    return has_block, dict(post.metadata), post.content, None


def _check_reserved(result: OKFValidationResult, md_file: Path, rel_path: str,
                    has_block: bool, meta: dict[str, Any], body: str) -> None:
    is_root_index = rel_path == "/index.md"
    if is_root_index:
        extra = set(meta) - {"okf_version"}
        if extra:
            result.errors.append(f"Reserved-file violation (§8): root index.md frontmatter may only "
                                 f"carry okf_version; found {sorted(extra)}.")
        version = meta.get("okf_version")
        if version is None:
            result.warnings.append("Root index.md should declare okf_version: \"0.2\".")
        elif str(version) != spec.OKF_VERSION:
            result.warnings.append(f"Root index.md declares okf_version {version!r}; this tool targets "
                                   f"{spec.OKF_VERSION} (consumers read other versions best-effort).")
    elif has_block or meta:
        result.errors.append(f"Reserved-file violation (§3.1/§8): only the root index.md may carry "
                             f"frontmatter; {md_file.name} at {rel_path} must not.")

    if md_file.name == "log.md":
        dates = [h for h in LOG_HEADING_PATTERN.findall(body)]
        bad = [d for d in dates if not spec.ISO_DATE_PATTERN.match(d)]
        if bad:
            result.warnings.append(f"log.md headings must be ISO YYYY-MM-DD (§9); found {bad}.")
        good = [d for d in dates if spec.ISO_DATE_PATTERN.match(d)]
        if good != sorted(good, reverse=True):
            result.warnings.append("log.md date headings must be newest first (§9).")


def _check_actor(result: OKFValidationResult, field_name: str, event: dict[str, Any]) -> None:
    actor = event.get("by")
    if not actor:
        result.warnings.append(f"`{field_name}` entry is missing required `by` (§5.2).")
    elif not spec.ACTOR_PATTERN.match(str(actor)):
        result.warnings.append(f"`{field_name}.by` value {actor!r} does not follow the actor "
                               f"convention human:<id> | process:<id> | <producer>/<version> (§7).")


def _check_concept(result: OKFValidationResult, rel_path: str, has_block: bool,
                   meta: dict[str, Any], body: str, known_ids: set[str],
                   today: dt.date) -> None:
    # §11 rule: frontmatter present
    if not has_block or not meta:
        result.errors.append("Conformance (§11): missing YAML frontmatter block.")

    # §4.1: `type` is the only required key and must be a non-empty string
    ctype = meta.get("type")
    if ctype is None or not str(ctype).strip():
        result.errors.append("Conformance (§4.1/§11): missing or empty required `type`.")
    elif not isinstance(ctype, str):
        result.warnings.append(f"`type` should be a short string (§4.1); got {type(ctype).__name__}.")

    # §10.2 Attested Computation
    if ctype == spec.ATTESTED_COMPUTATION_TYPE:
        if not str(meta.get("runtime") or "").strip():
            result.errors.append("Attested Computation (§10.2): missing required `runtime`.")
        has_body_computation = (spec.COMPUTATION_HEADING_PATTERN.search(body)
                                and spec.FENCED_BLOCK_PATTERN.search(body))
        if not meta.get("computation") and not has_body_computation:
            result.warnings.append("Attested Computation: no `computation` path and no `# Computation` "
                                   "heading with a fenced block in the body (§6.2/§10.2).")
    elif isinstance(ctype, str) and re.sub(r"[\s_-]+", "", ctype.lower()) == "attestedcomputation":
        result.warnings.append(f"`type: {ctype}` looks like an Attested Computation; the spec's exact "
                               f"type string is \"{spec.ATTESTED_COMPUTATION_TYPE}\" (§10.2). Consumers "
                               f"will treat this as an ordinary concept.")

    # §5.5 lifecycle
    status = meta.get("status")
    if status is not None and str(status) not in spec.VALID_STATUSES:
        result.warnings.append(f"`status: {status}` is not one of draft | stable | deprecated (§5.5).")
    if spec.effective_status(meta) == "deprecated":
        result.warnings.append("Lifecycle: concept is deprecated.")
    if "stale_after" in meta:
        iso = spec.to_iso_date(meta["stale_after"])
        if iso is None:
            result.warnings.append(f"`stale_after` must be YYYY-MM-DD (§5.5); got {meta['stale_after']!r}.")
        elif spec.is_stale(iso, today):
            result.warnings.append(f"Freshness: concept is STALE (stale_after {iso} <= today {today}).")

    # §5.2 trust
    generated = meta.get("generated")
    if generated is not None:
        if isinstance(generated, dict):
            _check_actor(result, "generated", generated)
        else:
            result.warnings.append("`generated` should be a mapping {by, at} (§5.2).")
    verified = spec.normalize_actor_events(meta.get("verified"))
    for event in verified:
        _check_actor(result, "verified", event)
    if not verified:
        result.warnings.append("Trust: no `verified` attestation (trust tier: unverified).")

    # §5.1 provenance
    sources = meta.get("sources")
    source_ids: set[str] = set()
    if sources is not None:
        if not isinstance(sources, list):
            result.warnings.append("`sources` should be a list (§5.1).")
        else:
            for i, src in enumerate(sources):
                if not isinstance(src, dict) or not str(src.get("resource") or "").strip():
                    result.warnings.append(f"`sources[{i}]` is missing `resource`, which the spec "
                                           f"REQUIRES within each entry (§5.1).")
                if isinstance(src, dict) and src.get("id"):
                    source_ids.add(str(src["id"]))
    prose = spec.FENCED_BLOCK_PATTERN.sub("", body)
    for ref in sorted(set(FOOTNOTE_REF_PATTERN.findall(prose))):
        if source_ids and ref not in source_ids:
            result.warnings.append(f"Footnote [^{ref}] has no matching `sources[].id` (§5.1).")

    # §6.1 links: broken links are tolerated by consumers but worth fixing
    for target in spec.extract_links(rel_path, body):
        if target not in known_ids:
            result.warnings.append(f"Broken link: /{target}.md does not exist in the bundle (§6.1).")


def validate_okf_bundle(bundle_dir: Path, today: dt.date | None = None) -> list[OKFValidationResult]:
    bundle_dir = Path(bundle_dir)
    if not bundle_dir.is_dir():
        raise FileNotFoundError(f"OKF bundle directory not found: {bundle_dir}")
    today = today or dt.date.today()

    files = sorted(bundle_dir.rglob("*.md"))
    known_ids = {spec.concept_id_from_rel_path(f.relative_to(bundle_dir).as_posix())
                 for f in files if f.name not in spec.RESERVED_FILES}

    results: list[OKFValidationResult] = []
    for md_file in files:
        rel_path = "/" + md_file.relative_to(bundle_dir).as_posix()
        reserved = md_file.name in spec.RESERVED_FILES
        result = OKFValidationResult(path=rel_path, kind="reserved" if reserved else "concept")

        has_block, meta, body, parse_error = _load(md_file)
        result.metadata = meta
        if parse_error:
            result.errors.append(f"Conformance (§11): {parse_error}")
            results.append(result)
            continue

        if reserved:
            _check_reserved(result, md_file, rel_path, has_block, meta, body)
        else:
            _check_concept(result, rel_path, has_block, meta, body, known_ids, today)
        results.append(result)

    if not (bundle_dir / "index.md").exists():
        results.insert(0, OKFValidationResult(
            path="/index.md", kind="reserved",
            warnings=["No root index.md: add one with okf_version: \"0.2\" for progressive disclosure (§8)."]))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an OKF v0.2 bundle.")
    parser.add_argument("bundle", nargs="?", default=os.getenv("OKF_BUNDLE_PATH", "okf_bundle"))
    parser.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    args = parser.parse_args(argv)

    results = validate_okf_bundle(Path(args.bundle))
    n_err = sum(len(r.errors) for r in results)
    n_warn = sum(len(r.warnings) for r in results)
    for r in results:
        label = "PASS" if r.valid else "FAIL"
        kind = r.metadata.get("type", "reserved") if r.kind == "concept" else "reserved"
        print(f"[{label}] {r.path} (type={kind})")
        for e in r.errors:
            print(f"    ERROR: {e}")
        for w in r.warnings:
            print(f"    WARN:  {w}")
    print(f"\n{len(results)} files, {n_err} error(s), {n_warn} warning(s)")
    if n_err or (args.strict and n_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
