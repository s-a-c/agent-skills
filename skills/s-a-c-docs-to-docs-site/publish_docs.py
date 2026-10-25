#!/usr/bin/env python3
"""Publish a project's docs tree into one owned docs-site namespace.

This helper deliberately does not know how to run Astro.  It only validates,
previews, and safely publishes source-owned Markdown links and generated public
files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCHEMA = "docs-to-docs-site"
VERSION = 1
NAMESPACE_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")


class PublishError(Exception):
    """A fail-closed validation or publication error."""


def absolute_path(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else Path.cwd() / path


def lexists(path: Path) -> bool:
    return os.path.lexists(path)


def is_descendant(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return path != root


def casefolded_path_parts(path: Path) -> tuple[str, ...]:
    """Return normalized path components for case-insensitive comparisons."""

    return tuple(part.casefold() for part in path.parts)


def paths_overlap(first: Path, second: Path) -> bool:
    first_parts = casefolded_path_parts(first)
    second_parts = casefolded_path_parts(second)
    if (
        first_parts == second_parts
        or first_parts[: len(second_parts)] == second_parts
        or second_parts[: len(first_parts)] == first_parts
    ):
        return True
    if lexists(first) and lexists(second):
        try:
            if os.path.samefile(first, second):
                return True
        except OSError:
            pass
    return False


def safe_relative(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise PublishError(f"invalid relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PublishError(f"invalid relative path: {value!r}")
    normalized = path.as_posix()
    if normalized != value:
        raise PublishError(f"non-normalized relative path: {value!r}")
    return value


def ensure_real_directory(path: Path, label: str) -> None:
    if path.is_symlink():
        raise PublishError(f"{label} must not be a symlink: {path}")
    if not path.exists() or not path.is_dir():
        raise PublishError(f"{label} is missing or not a directory: {path}")


def reject_symlink_components(path: Path, ancestor: Path, label: str) -> None:
    """Reject existing symlink components between an existing ancestor and path."""

    try:
        relative = path.relative_to(ancestor)
    except ValueError as exc:
        raise PublishError(f"{label} is outside its expected root: {path}") from exc
    current = ancestor
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise PublishError(f"{label} contains a symlink component: {current}")


class Config:
    def __init__(self, project_root: Path, docs_root: Path, site_root: Path, namespace: str) -> None:
        self.project_root = project_root
        self.docs_root = docs_root
        self.site_root = site_root
        self.namespace = namespace
        self.markdown_base = site_root / "src" / "content" / "docs"
        self.public_base = site_root / "public"
        self.markdown_root = self.markdown_base / namespace
        self.public_root = self.public_base / namespace
        self.state_root = site_root / ".docs-to-docs-site"
        self.manifest_path = self.state_root / f"{namespace}.json"
        self.lock_path = self.state_root / f"{namespace}.lock"

    def root_for(self, root: str) -> Path:
        if root == "markdown":
            return self.markdown_root
        if root == "public":
            return self.public_root
        raise PublishError(f"invalid destination root: {root!r}")


def validate_existing_directory_components(path: Path, ancestor: Path, label: str) -> None:
    """Reject existing file or symlink components before an apply can write."""

    try:
        relative = path.relative_to(ancestor)
    except ValueError as exc:
        raise PublishError(f"{label} is outside its expected root: {path}") from exc
    current = ancestor
    for part in relative.parts:
        current /= part
        if not lexists(current):
            break
        if current.is_symlink():
            raise PublishError(f"{label} contains a symlink component: {current}")
        if not current.is_dir():
            if current == path:
                raise PublishError(f"{label} is not a real directory: {current}")
            raise PublishError(f"{label} parent is not a real directory: {current}")


def validate_destination_layout(config: Config) -> None:
    for path, label in (
        (config.markdown_base, "src/content/docs root"),
        (config.public_base, "public root"),
        (config.state_root, "ownership state root"),
        (config.markdown_root, "Markdown namespace root"),
        (config.public_root, "public namespace root"),
    ):
        validate_existing_directory_components(path, config.site_root, label)
    if lexists(config.manifest_path) and (config.manifest_path.is_symlink() or not config.manifest_path.is_file()):
        raise PublishError(f"ownership manifest is not a regular file: {config.manifest_path}")


def make_config(args: argparse.Namespace) -> Config:
    if not NAMESPACE_RE.fullmatch(args.namespace):
        raise PublishError(
            "namespace must be a lowercase kebab-case slug containing only letters, digits, and single hyphens"
        )

    project_input = absolute_path(args.project_root)
    site_input = absolute_path(args.site_root or "~/infra/docs-site")
    if project_input.is_symlink():
        raise PublishError(f"project root must not be a symlink: {project_input}")
    if site_input.is_symlink():
        raise PublishError(f"site root must not be a symlink: {site_input}")
    ensure_real_directory(project_input, "project root")
    ensure_real_directory(site_input, "site root")

    project_root = project_input.resolve(strict=True)
    site_root = site_input.resolve(strict=True)
    docs_root = project_root / "docs"
    if docs_root.is_symlink():
        raise PublishError(f"docs root must not be a symlink: {docs_root}")
    ensure_real_directory(docs_root, "docs root")
    docs_root = docs_root.resolve(strict=True)

    if paths_overlap(project_root, site_root) or paths_overlap(docs_root, site_root):
        raise PublishError("project/docs source and site root must not overlap")

    config = Config(project_root, docs_root, site_root, args.namespace)
    validate_destination_layout(config)
    return config


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk_sources(docs_root: Path) -> list[Path]:
    files: list[Path] = []
    seen_components: dict[tuple[str, ...], tuple[str, str]] = {}

    def visit(directory: Path) -> None:
        try:
            children = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            raise PublishError(f"cannot read docs source {directory}: {exc}") from exc
        for child in children:
            path = Path(child.path)
            if child.is_symlink():
                raise PublishError(f"source symlinks are not allowed: {path}")
            relative = safe_relative(path.relative_to(docs_root).as_posix())
            folded_components = casefolded_path_parts(PurePosixPath(relative))
            entry_kind = "directory" if child.is_dir(follow_symlinks=False) else "file"
            previous = seen_components.get(folded_components)
            if previous is not None and previous[1] != relative:
                if previous[0] == "directory" or entry_kind == "directory":
                    raise PublishError(f"source directory component case collision: {previous[1]} and {relative}")
                raise PublishError(f"source path/case collision: {previous[1]} and {relative}")
            seen_components[folded_components] = (entry_kind, relative)
            if child.is_dir(follow_symlinks=False):
                visit(path)
            elif child.is_file(follow_symlinks=False):
                files.append(path)
            else:
                raise PublishError(f"unsupported source entry (not a regular file): {path}")

    visit(docs_root)
    if not files:
        raise PublishError(f"docs root is empty: {docs_root}")
    return sorted(files, key=lambda path: path.relative_to(docs_root).as_posix())


def expected_entries(config: Config, source_files: Iterable[Path]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for source in source_files:
        relative = source.relative_to(config.docs_root).as_posix()
        suffix = source.suffix.lower()
        if suffix == ".md":
            root = "markdown"
            entry_class = "markdown"
            integration = "symlink"
            target = str(source.resolve(strict=True))
        elif suffix == ".html":
            root = "public"
            entry_class = "html"
            integration = "generated-copy"
            target = None
        else:
            root = "public"
            entry_class = "asset"
            integration = "generated-copy"
            target = None
        entry: dict[str, Any] = {
            "class": entry_class,
            "destination_rel": relative,
            "integration": integration,
            "root": root,
            "sha256": sha256_file(source),
            "size": source.stat().st_size,
            "source_rel": relative,
        }
        if target is not None:
            entry["symlink_target"] = target
        entries.append(entry)
    return sorted(entries, key=lambda entry: (entry["root"], entry["destination_rel"]))


def manifest_payload(config: Config, entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "destination_roots": {
            "markdown": str(config.markdown_root),
            "public": str(config.public_root),
        },
        "docs_root_realpath": str(config.docs_root),
        "entries": entries,
        "manifest_path": str(config.manifest_path),
        "namespace": config.namespace,
        "project_root_realpath": str(config.project_root),
        "schema": SCHEMA,
        "version": VERSION,
    }


def load_prior(config: Config) -> dict[str, Any] | None:
    if not lexists(config.manifest_path):
        return None
    if config.manifest_path.is_symlink() or not config.manifest_path.is_file():
        raise PublishError(f"ownership manifest is not a regular file: {config.manifest_path}")
    try:
        with config.manifest_path.open("r", encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, ValueError) as exc:
        raise PublishError(f"cannot read ownership manifest: {config.manifest_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PublishError("ownership manifest must contain a JSON object")
    return value


def entry_key(entry: dict[str, Any]) -> tuple[str, str]:
    return entry["root"], entry["destination_rel"]


def validate_prior(config: Config, prior: dict[str, Any] | None) -> dict[tuple[str, str], dict[str, Any]]:
    if prior is None:
        return {}
    required = {
        "schema",
        "version",
        "namespace",
        "project_root_realpath",
        "docs_root_realpath",
        "destination_roots",
        "manifest_path",
        "entries",
    }
    if set(prior) < required:
        missing = sorted(required - set(prior))
        raise PublishError(f"ownership manifest is incomplete; missing: {', '.join(missing)}")
    if not isinstance(prior["schema"], str) or not isinstance(prior["version"], int) or isinstance(prior["version"], bool):
        raise PublishError("ownership manifest schema/version types are invalid")
    if not isinstance(prior["namespace"], str):
        raise PublishError("ownership manifest namespace must be a string")
    if not isinstance(prior["project_root_realpath"], str) or not isinstance(prior["docs_root_realpath"], str):
        raise PublishError("ownership manifest project/docs identity must be strings")
    if not isinstance(prior["destination_roots"], dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in prior["destination_roots"].items()
    ):
        raise PublishError("ownership manifest destination roots must be an object of strings")
    if not isinstance(prior["manifest_path"], str):
        raise PublishError("ownership manifest path must be a string")
    if prior["schema"] != SCHEMA or prior["version"] != VERSION:
        raise PublishError("ownership manifest schema/version does not match this helper")
    if prior["namespace"] != config.namespace:
        raise PublishError("ownership manifest namespace does not match the requested namespace")
    if prior["project_root_realpath"] != str(config.project_root) or prior["docs_root_realpath"] != str(config.docs_root):
        raise PublishError("ownership manifest project/docs identity does not match the source")
    expected_roots = {
        "markdown": str(config.markdown_root),
        "public": str(config.public_root),
    }
    if prior["destination_roots"] != expected_roots or prior["manifest_path"] != str(config.manifest_path):
        raise PublishError("ownership manifest destination roots do not match the requested site")
    entries = prior["entries"]
    if not isinstance(entries, list):
        raise PublishError("ownership manifest entries must be a list")

    result: dict[tuple[str, str], dict[str, Any]] = {}
    folded: dict[tuple[str, str], str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise PublishError("ownership manifest contains a non-object entry")
        entry_required = {"class", "destination_rel", "integration", "root", "sha256", "size", "source_rel"}
        if set(entry) < entry_required:
            raise PublishError("ownership manifest contains an incomplete entry")
        relative = safe_relative(entry["destination_rel"])
        source_rel = safe_relative(entry["source_rel"])
        if source_rel != relative:
            raise PublishError("ownership manifest source/destination paths do not correspond")
        root = entry["root"]
        entry_class = entry["class"]
        integration = entry["integration"]
        if not isinstance(root, str) or root not in {"markdown", "public"}:
            raise PublishError("ownership manifest contains an invalid root")
        if not isinstance(entry_class, str) or not isinstance(integration, str):
            raise PublishError(f"ownership manifest class/integration types are invalid for {relative}")
        suffix = Path(relative).suffix.lower()
        expected_class = "markdown" if suffix == ".md" else "html" if suffix == ".html" else "asset"
        expected_root = "markdown" if expected_class == "markdown" else "public"
        expected_integration = "symlink" if expected_class == "markdown" else "generated-copy"
        if entry_class != expected_class or root != expected_root or integration != expected_integration:
            raise PublishError(f"ownership manifest class/root mismatch for {relative}")
        if not isinstance(entry["size"], int) or isinstance(entry["size"], bool) or entry["size"] < 0:
            raise PublishError(f"ownership manifest size is invalid for {relative}")
        if not isinstance(entry["sha256"], str) or not HASH_RE.fullmatch(entry["sha256"]):
            raise PublishError(f"ownership manifest hash is invalid for {relative}")
        source = config.docs_root / PurePosixPath(relative)
        destination = config.root_for(root) / PurePosixPath(relative)
        if not is_descendant(destination, config.root_for(root)):
            raise PublishError(f"ownership manifest destination escapes its root: {relative}")
        if expected_class == "markdown":
            expected_target = str(source.resolve(strict=False))
            if not isinstance(entry.get("symlink_target"), str) or entry["symlink_target"] != expected_target:
                raise PublishError(f"ownership manifest Markdown target is invalid for {relative}")
        elif "symlink_target" in entry:
            raise PublishError(f"ownership manifest copy entry has a symlink target: {relative}")
        key = (root, relative)
        folded_key = (root, relative.casefold())
        if key in result or folded_key in folded:
            raise PublishError(f"ownership manifest path/case collision: {relative}")
        result[key] = entry
        folded[folded_key] = relative

    ordered = sorted(result, key=lambda key: key)
    if list(result) != ordered:
        raise PublishError("ownership manifest entries are not sorted")
    return result


def iter_live_leaves(root: Path) -> list[tuple[str, Path]]:
    if not lexists(root):
        return []
    if root.is_symlink() or not root.is_dir():
        raise PublishError(f"destination namespace root is not a real directory: {root}")
    leaves: list[tuple[str, Path]] = []

    def visit(directory: Path) -> None:
        try:
            children = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            raise PublishError(f"cannot scan destination namespace {directory}: {exc}") from exc
        for child in children:
            path = Path(child.path)
            relative = path.relative_to(root).as_posix()
            if child.is_symlink():
                leaves.append((relative, path))
            elif child.is_dir(follow_symlinks=False):
                visit(path)
            else:
                leaves.append((relative, path))

    visit(root)
    return leaves


def actual_matches(entry: dict[str, Any], destination: Path) -> bool:
    if not lexists(destination):
        return False
    if entry["integration"] == "symlink":
        return destination.is_symlink() and os.readlink(destination) == entry["symlink_target"]
    return (
        not destination.is_symlink()
        and destination.is_file()
        and destination.stat().st_size == entry["size"]
        and sha256_file(destination) == entry["sha256"]
    )


def entry_signature(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (
        entry["class"],
        entry["integration"],
        entry["root"],
        entry["sha256"],
        entry["size"],
        entry.get("symlink_target"),
    )


def label(root: str, relative: str) -> str:
    return f"{root}:{relative}"


def analyze(
    config: Config, expected: list[dict[str, Any]], prior: dict[str, Any] | None
) -> tuple[dict[str, Any], dict[tuple[str, str], dict[str, Any]]]:
    prior_entries = validate_prior(config, prior)
    expected_entries_by_key = {entry_key(entry): entry for entry in expected}
    errors: list[str] = []
    live: dict[tuple[str, str], Path] = {}
    live_folded: dict[tuple[str, str], str] = {}
    for root in ("markdown", "public"):
        for relative, path in iter_live_leaves(config.root_for(root)):
            key = (root, relative)
            folded_key = (root, relative.casefold())
            if folded_key in live_folded:
                errors.append(f"destination path/case collision: {live_folded[folded_key]} and {relative}")
            live_folded[folded_key] = relative
            live[key] = path
            prior_entry = prior_entries.get(key)
            if prior_entry is None:
                errors.append(f"unowned destination collision: {label(root, relative)}")
            elif not actual_matches(prior_entry, path):
                errors.append(f"owned destination drift: {label(root, relative)}")

    stale_keys = sorted(set(prior_entries) - set(expected_entries_by_key))
    stale = [label(root, relative) for root, relative in stale_keys]
    additions: list[str] = []
    replacements: list[str] = []
    unchanged: list[str] = []
    for entry in expected:
        key = entry_key(entry)
        current = live.get(key)
        previous = prior_entries.get(key)
        item = label(*key)
        if current is None:
            if previous is None:
                additions.append(item)
            else:
                errors.append(f"owned destination is missing: {item}")
        elif previous is None:
            # The collision is already reported by the live scan; leave this out
            # of additions/replacements so a failure cannot look actionable.
            continue
        elif entry_signature(entry) == entry_signature(previous):
            unchanged.append(item)
        else:
            replacements.append(item)
        if current is not None and previous is not None and not actual_matches(previous, current):
            # The live scan already reports this, but avoid duplicate messages.
            pass

    report = {
        "additions": additions,
        "applied": False,
        "errors": sorted(set(errors)),
        "mode": "preview",
        "namespace": config.namespace,
        "replacements": replacements,
        "stale_owned": stale,
        "unchanged": unchanged,
        "warnings": [],
    }
    return report, prior_entries


def ensure_parent(destination: Path, root: Path) -> None:
    if not lexists(root):
        missing: list[Path] = []
        current = root
        while not lexists(current):
            missing.append(current)
            parent = current.parent
            if parent == current:
                raise PublishError(f"cannot create destination root: {root}")
            current = parent
        if current.is_symlink() or not current.is_dir():
            raise PublishError(f"destination root parent is not a real directory: {current}")
        for path in reversed(missing):
            path.mkdir()
    elif root.is_symlink() or not root.is_dir():
        raise PublishError(f"destination root is not a real directory: {root}")
    try:
        relative_parent = destination.parent.relative_to(root)
    except ValueError as exc:
        raise PublishError(f"destination parent escapes root: {destination}") from exc
    current = root
    for part in relative_parent.parts:
        current /= part
        if lexists(current):
            if current.is_symlink() or not current.is_dir():
                raise PublishError(f"destination parent is not a real directory: {current}")
        else:
            current.mkdir()


def clone_path(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        os.symlink(os.readlink(source), destination)
    elif source.is_file():
        shutil.copy2(source, destination)
    else:
        raise PublishError(f"cannot back up non-file destination: {source}")


def stage_entries(config: Config, entries: list[dict[str, Any]], stage_root: Path) -> None:
    for entry in entries:
        source = config.docs_root / PurePosixPath(entry["source_rel"])
        destination = stage_root / entry["root"] / config.namespace / PurePosixPath(entry["destination_rel"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        if entry["integration"] == "symlink":
            os.symlink(entry["symlink_target"], destination)
        else:
            shutil.copy2(source, destination)


def acquire_apply_lock(config: Config) -> None:
    ensure_parent(config.lock_path, config.site_root)
    try:
        config.lock_path.mkdir()
    except FileExistsError as exc:
        raise PublishError(f"publication lock is already held: {config.lock_path}") from exc


def release_apply_lock(config: Config) -> None:
    try:
        config.lock_path.rmdir()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise PublishError(f"cannot release publication lock: {config.lock_path}: {exc}") from exc


def apply_publication(
    config: Config,
    entries: list[dict[str, Any]],
    prior_entries: dict[tuple[str, str], dict[str, Any]],
    stale: list[str],
    lock_held: bool = False,
) -> None:
    payload = manifest_payload(config, entries)
    if not lock_held:
        acquire_apply_lock(config)
    try:
        with tempfile.TemporaryDirectory(prefix=".docs-to-docs-site-", dir=str(config.site_root.parent)) as temporary:
            transaction = Path(temporary)
            stage = transaction / "stage"
            backup = transaction / "backup"
            stage_entries(config, entries, stage)
            staged_manifest = transaction / "manifest.json"
            staged_manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            changed: list[tuple[Path, Path | None, Path, dict[str, Any] | None, bool]] = []
            manifest_backup: Path | None = None
            manifest_committed = False

            def backup_destination(destination: Path, index: int) -> Path:
                saved = backup / f"destination-{index}"
                clone_path(destination, saved)
                return saved

            def remove_current(path: Path) -> None:
                if lexists(path):
                    if path.is_dir() and not path.is_symlink():
                        raise PublishError(f"refusing to remove directory: {path}")
                    path.unlink()

            def rollback() -> None:
                conflicts: list[str] = []
                if manifest_committed:
                    manifest_safe = False
                    if not lexists(config.manifest_path):
                        conflicts.append(f"ownership manifest missing during rollback: {config.manifest_path}")
                    else:
                        try:
                            with config.manifest_path.open("r", encoding="utf-8") as stream:
                                manifest_safe = (
                                    not config.manifest_path.is_symlink()
                                    and config.manifest_path.is_file()
                                    and json.load(stream) == payload
                                )
                        except (OSError, ValueError, TypeError):
                            manifest_safe = False
                        if not manifest_safe:
                            conflicts.append(f"ownership manifest drifted: {config.manifest_path}")
                        else:
                            try:
                                config.manifest_path.unlink()
                            except OSError as exc:
                                manifest_safe = False
                                conflicts.append(f"could not remove published ownership manifest: {exc}")
                    if manifest_safe and manifest_backup is not None:
                        try:
                            ensure_parent(config.manifest_path, config.state_root)
                            os.replace(manifest_backup, config.manifest_path)
                        except (OSError, PublishError) as exc:
                            conflicts.append(f"could not restore ownership manifest: {exc}")
                for destination, saved, root, expected, removed_by_transaction in reversed(changed):
                    if not lexists(destination):
                        if removed_by_transaction and saved is not None:
                            try:
                                ensure_parent(destination, root)
                                os.replace(saved, destination)
                            except (OSError, PublishError) as exc:
                                conflicts.append(f"could not restore destination {destination}: {exc}")
                        elif saved is not None:
                            conflicts.append(f"destination missing during rollback: {destination}")
                        continue
                    if expected is None:
                        conflicts.append(f"destination appeared during rollback: {destination}")
                        continue
                    try:
                        matches = actual_matches(expected, destination)
                    except OSError as exc:
                        matches = False
                        conflicts.append(f"could not verify rollback identity for {destination}: {exc}")
                    if not matches:
                        if not any(str(destination) in conflict for conflict in conflicts):
                            conflicts.append(f"destination drifted during rollback: {destination}")
                        continue
                    try:
                        if destination.is_dir() and not destination.is_symlink():
                            raise PublishError(f"refusing to remove directory: {destination}")
                        destination.unlink()
                    except (OSError, PublishError) as exc:
                        conflicts.append(f"could not remove published destination {destination}: {exc}")
                        continue
                    if saved is not None:
                        try:
                            ensure_parent(destination, root)
                            os.replace(saved, destination)
                        except (OSError, PublishError) as exc:
                            conflicts.append(f"could not restore destination {destination}: {exc}")
                if conflicts:
                    raise PublishError("rollback conflict; preserved live edits: " + "; ".join(sorted(set(conflicts))))

            try:
                for index, entry in enumerate(entries):
                    destination = config.root_for(entry["root"]) / PurePosixPath(entry["destination_rel"])
                    root = config.root_for(entry["root"])
                    ensure_parent(destination, root)
                    saved = backup_destination(destination, index) if lexists(destination) else None
                    stage_path = stage / entry["root"] / config.namespace / PurePosixPath(entry["destination_rel"])
                    os.replace(stage_path, destination)
                    changed.append((destination, saved, root, entry, False))

                for offset, stale_label in enumerate(stale, start=len(entries)):
                    root_name, relative = stale_label.split(":", 1)
                    destination = config.root_for(root_name) / PurePosixPath(relative)
                    if not lexists(destination):
                        continue
                    prior_entry = prior_entries.get((root_name, relative))
                    if prior_entry is None:
                        raise PublishError(f"stale path is not owned by the matching manifest: {stale_label}")
                    ensure_parent(destination, config.root_for(root_name))
                    saved = backup_destination(destination, offset)
                    remove_current(destination)
                    changed.append((destination, saved, config.root_for(root_name), prior_entry, True))

                if lexists(config.manifest_path):
                    manifest_backup = backup / "manifest"
                    clone_path(config.manifest_path, manifest_backup)
                ensure_parent(config.manifest_path, config.state_root)
                os.replace(staged_manifest, config.manifest_path)
                manifest_committed = True
                smoke_check(config, entries)
            except BaseException as original:
                try:
                    rollback()
                except PublishError as rollback_error:
                    raise PublishError(f"{original}; {rollback_error}") from original
                raise
    finally:
        if not lock_held:
            release_apply_lock(config)


def smoke_check(config: Config, entries: list[dict[str, Any]]) -> None:
    for entry in entries:
        destination = config.root_for(entry["root"]) / PurePosixPath(entry["destination_rel"])
        if not actual_matches(entry, destination):
            raise PublishError(f"post-publication verification failed: {label(entry['root'], entry['destination_rel'])}")
    try:
        with config.manifest_path.open("r", encoding="utf-8") as stream:
            manifest = json.load(stream)
    except (OSError, ValueError) as exc:
        raise PublishError(f"post-publication manifest verification failed: {exc}") from exc
    if manifest != manifest_payload(config, entries):
        raise PublishError("post-publication manifest does not match the expected ownership manifest")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Preview or safely publish one project's docs/ tree into an owned docs-site namespace."
    )
    result.add_argument("--project-root", required=True, help="Project directory containing docs/")
    result.add_argument("--namespace", required=True, help="Lowercase kebab-case destination namespace")
    result.add_argument("--site-root", help="Existing docs-site root (default: ~/infra/docs-site)")
    result.add_argument("--apply", action="store_true", help="Write the staged publication")
    result.add_argument("--prune", action="store_true", help="Delete stale paths owned by the matching manifest")
    return result


def error_report(message: str, namespace: str | None = None) -> dict[str, Any]:
    return {
        "additions": [],
        "applied": False,
        "errors": [message],
        "mode": "preview",
        "namespace": namespace,
        "replacements": [],
        "stale_owned": [],
        "unchanged": [],
        "warnings": [],
    }


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.prune and not args.apply:
        report = error_report("--prune requires --apply", args.namespace)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    try:
        config = make_config(args)
        lock_held = False
        if args.apply:
            acquire_apply_lock(config)
            lock_held = True
        try:
            sources = walk_sources(config.docs_root)
            entries = expected_entries(config, sources)
            prior = load_prior(config)
            report, prior_entries = analyze(config, entries, prior)
            report["mode"] = "apply" if args.apply else "preview"
            if report["stale_owned"] and not (args.apply and args.prune):
                report["errors"].append("stale owned files require --apply --prune")
                report["errors"] = sorted(set(report["errors"]))
            if report["errors"]:
                print(json.dumps(report, indent=2, sort_keys=True))
                return 1
            if args.apply:
                stale = report["stale_owned"]
                apply_publication(config, entries, prior_entries, stale, lock_held=True)
                report["applied"] = True
                report["mode"] = "apply"
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0
        finally:
            if lock_held:
                release_apply_lock(config)
    except (OSError, PublishError, TypeError, ValueError, KeyError, UnicodeError) as exc:
        report = error_report(str(exc), getattr(args, "namespace", None))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
