#!/usr/bin/env python3
"""Focused subprocess tests for publish_docs.py."""

from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent
HELPER = HERE / "publish_docs.py"


class PublishDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.site = self.root / "docs-site"
        self.project.mkdir()
        self.site.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_docs(self, **files: str) -> None:
        docs = self.project / "docs"
        docs.mkdir(exist_ok=True)
        for relative, content in files.items():
            path = docs / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def run_helper(self, namespace: str = "demo", *flags: str, site: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [
            sys.executable,
            str(HELPER),
            "--project-root",
            str(self.project),
            "--namespace",
            namespace,
            "--site-root",
            str(site or self.site),
            *flags,
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        report = json.loads(result.stdout) if result.stdout.strip().startswith("{") else {}
        return result, report

    def load_helper_module(self):
        spec = importlib.util.spec_from_file_location("publish_docs_under_test", HELPER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_help(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HELPER), "--help"], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--project-root", result.stdout)
        self.assertIn("--apply", result.stdout)
        self.assertIn("--prune", result.stdout)

    def test_missing_docs_is_rejected(self) -> None:
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("docs root" in error for error in report["errors"]))

    def test_empty_docs_is_rejected(self) -> None:
        (self.project / "docs").mkdir()
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("empty" in error for error in report["errors"]))

    def test_symlinked_content_root_is_rejected(self) -> None:
        self.write_docs(page="# Page\n")
        target = self.root / "outside-content"
        target.mkdir()
        (self.site / "src" / "content").mkdir(parents=True)
        os.symlink(target, self.site / "src" / "content" / "docs")
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("symlink" in error for error in report["errors"]))

    def test_source_symlink_is_rejected(self) -> None:
        self.write_docs(page="# Page\n")
        os.symlink(self.project / "docs" / "page.md", self.project / "docs" / "alias.md")
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("source symlink" in error for error in report["errors"]))

    def test_invalid_namespace_is_rejected(self) -> None:
        self.write_docs(page="# Page\n")
        result, report = self.run_helper("Bad_Name")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("namespace" in error for error in report["errors"]))

    def test_source_site_overlap_is_rejected(self) -> None:
        self.write_docs(page="# Page\n")
        nested_site = self.project / "site"
        nested_site.mkdir()
        result, report = self.run_helper(site=nested_site)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("overlap" in error for error in report["errors"]))

    def test_source_case_collision_is_rejected(self) -> None:
        self.write_docs(**{"Guide.md": "# A\n", "guide.md": "# B\n"})
        try:
            same_file = os.path.samefile(self.project / "docs" / "Guide.md", self.project / "docs" / "guide.md")
        except FileNotFoundError:
            same_file = False
        if same_file:
            self.skipTest("filesystem is case-insensitive")
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("case collision" in error for error in report["errors"]))

    def test_source_directory_component_case_collision_is_rejected(self) -> None:
        self.write_docs(**{"A/one.md": "# A\n", "a/two.md": "# B\n"})
        try:
            same_directory = os.path.samefile(self.project / "docs" / "A", self.project / "docs" / "a")
        except FileNotFoundError:
            same_directory = False
        if same_directory:
            self.skipTest("filesystem is case-insensitive")
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("directory component case collision" in error for error in report["errors"]))

    def test_preview_rejects_unsafe_destination_parent(self) -> None:
        self.write_docs(page="# Page\n")
        (self.site / "public").write_text("not a directory\n", encoding="utf-8")
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("public root" in error and "directory" in error for error in report["errors"]))
        self.assertFalse((self.site / ".docs-to-docs-site").exists())

    def test_preview_rejects_unsafe_namespace_root(self) -> None:
        self.write_docs(page="# Page\n")
        public = self.site / "public"
        public.mkdir()
        outside = self.root / "outside-public"
        outside.mkdir()
        os.symlink(outside, public / "demo")
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("public namespace root" in error for error in report["errors"]))

    def test_preview_makes_no_writes(self) -> None:
        self.write_docs(**{"guide/page.md": "# Page\n", "guide/page.html": "<h1>Page</h1>\n", "guide/app.css": "body{}\n"})
        before = sorted(path.relative_to(self.site).as_posix() for path in self.site.rglob("*"))
        result, report = self.run_helper()
        after = sorted(path.relative_to(self.site).as_posix() for path in self.site.rglob("*"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(before, after)
        self.assertFalse((self.site / ".docs-to-docs-site").exists())
        self.assertEqual(len(report["additions"]), 3)

    def test_apply_refuses_held_lock_without_changing_destinations(self) -> None:
        self.write_docs(page="# Page\n")
        existing = self.site / "public" / "demo" / "existing.txt"
        existing.parent.mkdir(parents=True)
        existing.write_text("keep\n", encoding="utf-8")
        lock = self.site / ".docs-to-docs-site" / "demo.lock"
        lock.parent.mkdir()
        lock.mkdir()
        before = sorted(path.relative_to(self.site).as_posix() for path in self.site.rglob("*"))

        result, report = self.run_helper("demo", "--apply")

        after = sorted(path.relative_to(self.site).as_posix() for path in self.site.rglob("*"))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertTrue(any("publication lock is already held" in error for error in report["errors"]))
        self.assertEqual(before, after)
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep\n")

    def test_fresh_apply_links_markdown_copies_public_and_writes_manifest(self) -> None:
        self.write_docs(**{"guide/page.md": "# Page\n", "guide/page.html": "<h1>Page</h1>\n", "guide/app.css": "body{}\n"})
        result, report = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        markdown = self.site / "src" / "content" / "docs" / "demo" / "guide" / "page.md"
        html = self.site / "public" / "demo" / "guide" / "page.html"
        asset = self.site / "public" / "demo" / "guide" / "app.css"
        self.assertTrue(markdown.is_symlink())
        self.assertEqual(Path(os.readlink(markdown)), (self.project / "docs" / "guide" / "page.md").resolve())
        self.assertEqual(html.read_text(encoding="utf-8"), "<h1>Page</h1>\n")
        self.assertEqual(asset.read_text(encoding="utf-8"), "body{}\n")
        manifest_path = self.site / ".docs-to-docs-site" / "demo.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertTrue(report["applied"])
        self.assertEqual(manifest["schema"], "docs-to-docs-site")
        self.assertEqual(manifest["namespace"], "demo")
        self.assertEqual(manifest["docs_root_realpath"], str((self.project / "docs").resolve()))
        self.assertEqual({entry["destination_rel"] for entry in manifest["entries"]}, {"guide/page.md", "guide/page.html", "guide/app.css"})
        markdown_entry = next(entry for entry in manifest["entries"] if entry["class"] == "markdown")
        self.assertEqual(markdown_entry["symlink_target"], str((self.project / "docs" / "guide" / "page.md").resolve()))

    def test_unowned_collision_refuses_apply(self) -> None:
        self.write_docs(page="# Page\n")
        collision = self.site / "public" / "demo" / "extra.txt"
        collision.parent.mkdir(parents=True)
        collision.write_text("keep\n", encoding="utf-8")
        result, report = self.run_helper("demo", "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("unowned" in error for error in report["errors"]))
        self.assertFalse((self.site / "src" / "content" / "docs" / "demo" / "page.md").exists())

    def test_drift_refuses_replacement(self) -> None:
        self.write_docs(page="# Page\n", **{"page.html": "original\n"})
        result, _ = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        destination = self.site / "public" / "demo" / "page.html"
        destination.write_text("local edit\n", encoding="utf-8")
        result, report = self.run_helper("demo", "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("drift" in error for error in report["errors"]))
        self.assertEqual(destination.read_text(encoding="utf-8"), "local edit\n")

    def test_malformed_manifest_fields_return_json_error(self) -> None:
        self.write_docs(page="# Page\n")
        result, _ = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest_path = self.site / ".docs-to-docs-site" / "demo.json"
        original = json.loads(manifest_path.read_text(encoding="utf-8"))
        for field, value in (("root", []), ("class", []), ("sha256", []), ("size", "wrong")):
            with self.subTest(field=field):
                malformed = json.loads(json.dumps(original))
                malformed["entries"][0][field] = value
                manifest_path.write_text(json.dumps(malformed), encoding="utf-8")
                result, report = self.run_helper()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stderr, "")
                self.assertTrue(report.get("errors"))
        manifest_path.write_text(json.dumps(original), encoding="utf-8")

    def test_rollback_preserves_destination_drift(self) -> None:
        self.write_docs(**{"page.html": "original\n"})
        result, _ = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        destination = self.site / "public" / "demo" / "page.html"
        (self.project / "docs" / "page.html").write_text("updated\n", encoding="utf-8")

        helper = self.load_helper_module()
        config = helper.make_config(
            SimpleNamespace(project_root=str(self.project), site_root=str(self.site), namespace="demo")
        )
        entries = helper.expected_entries(config, helper.walk_sources(config.docs_root))
        prior = helper.load_prior(config)
        report, prior_entries = helper.analyze(config, entries, prior)
        self.assertIn("public:page.html", report["replacements"])
        original_smoke_check = helper.smoke_check

        def fail_after_user_edit(config, entries):
            destination.write_text("local edit\n", encoding="utf-8")
            raise helper.PublishError("forced smoke-check failure")

        helper.smoke_check = fail_after_user_edit
        try:
            with self.assertRaises(helper.PublishError) as failure:
                helper.apply_publication(config, entries, prior_entries, report["stale_owned"])
        finally:
            helper.smoke_check = original_smoke_check
        self.assertIn("rollback conflict", str(failure.exception))
        self.assertEqual(destination.read_text(encoding="utf-8"), "local edit\n")

    def test_rollback_preserves_destination_deletion(self) -> None:
        self.write_docs(**{"page.html": "original\n"})
        result, _ = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        destination = self.site / "public" / "demo" / "page.html"
        (self.project / "docs" / "page.html").write_text("updated\n", encoding="utf-8")

        helper = self.load_helper_module()
        config = helper.make_config(
            SimpleNamespace(project_root=str(self.project), site_root=str(self.site), namespace="demo")
        )
        entries = helper.expected_entries(config, helper.walk_sources(config.docs_root))
        prior = helper.load_prior(config)
        report, prior_entries = helper.analyze(config, entries, prior)
        self.assertIn("public:page.html", report["replacements"])
        original_smoke_check = helper.smoke_check

        def fail_after_user_deletion(config, entries):
            destination.unlink()
            raise helper.PublishError("forced smoke-check failure")

        helper.smoke_check = fail_after_user_deletion
        try:
            with self.assertRaises(helper.PublishError) as failure:
                helper.apply_publication(config, entries, prior_entries, report["stale_owned"])
        finally:
            helper.smoke_check = original_smoke_check
        self.assertIn("rollback conflict", str(failure.exception))
        self.assertFalse(destination.exists())

    def test_rollback_restores_stale_pruned_destination(self) -> None:
        self.write_docs(**{"keep.md": "# Keep\n", "remove.html": "remove\n"})
        result, _ = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        destination = self.site / "public" / "demo" / "remove.html"
        (self.project / "docs" / "remove.html").unlink()

        helper = self.load_helper_module()
        config = helper.make_config(
            SimpleNamespace(project_root=str(self.project), site_root=str(self.site), namespace="demo")
        )
        entries = helper.expected_entries(config, helper.walk_sources(config.docs_root))
        prior = helper.load_prior(config)
        report, prior_entries = helper.analyze(config, entries, prior)
        self.assertIn("public:remove.html", report["stale_owned"])
        original_smoke_check = helper.smoke_check

        def fail_after_prune(config, entries):
            self.assertFalse(destination.exists())
            raise helper.PublishError("forced smoke-check failure")

        helper.smoke_check = fail_after_prune
        try:
            with self.assertRaises(helper.PublishError) as failure:
                helper.apply_publication(config, entries, prior_entries, report["stale_owned"])
        finally:
            helper.smoke_check = original_smoke_check
        self.assertIn("forced smoke-check failure", str(failure.exception))
        self.assertEqual(destination.read_text(encoding="utf-8"), "remove\n")

    def test_stale_requires_prune(self) -> None:
        self.write_docs(**{"keep.md": "# Keep\n", "remove.html": "remove\n"})
        result, _ = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (self.project / "docs" / "remove.html").unlink()
        result, report = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public:remove.html", report["stale_owned"])
        self.assertTrue(any("--apply --prune" in error for error in report["errors"]))
        self.assertTrue((self.site / "public" / "demo" / "remove.html").exists())

    def test_prune_removes_only_owned_stale_files(self) -> None:
        self.write_docs(**{"keep.md": "# Keep\n", "remove.html": "remove\n"})
        result, _ = self.run_helper("demo", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        unrelated = self.site / "public" / "unowned" / "keep.txt"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("do not remove\n", encoding="utf-8")
        (self.project / "docs" / "remove.html").unlink()
        result, report = self.run_helper("demo", "--apply", "--prune")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["applied"])
        self.assertFalse((self.site / "public" / "demo" / "remove.html").exists())
        self.assertTrue((self.site / "src" / "content" / "docs" / "demo" / "keep.md").is_symlink())
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "do not remove\n")
        manifest = json.loads((self.site / ".docs-to-docs-site" / "demo.json").read_text(encoding="utf-8"))
        self.assertNotIn("remove.html", {entry["destination_rel"] for entry in manifest["entries"]})

    def test_prune_requires_apply(self) -> None:
        self.write_docs(page="# Page\n")
        result, report = self.run_helper("demo", "--prune")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--prune requires --apply", report["errors"])


if __name__ == "__main__":
    unittest.main()
