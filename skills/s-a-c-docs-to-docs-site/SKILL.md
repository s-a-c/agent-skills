---
name: s-a-c-docs-to-docs-site
description: Use when a project's docs/ tree must be published into a namespaced docs-site destination with Markdown source integration, HTML/assets, ownership checks, or an explicit Astro handoff.
---

# Docs to Docs Site

Publish one project's source-owned `docs/` tree into a single namespace without
copying authored Markdown into the site repository or editing shared Astro
configuration. The helper is intentionally independent of Astro, installs,
service restarts, and root migration.

## 1. Helper command

Run from the skill directory, or provide its absolute path:

```sh
python3 publish_docs.py --project-root PATH --namespace SLUG \
  [--site-root PATH] [--apply] [--prune]
```

`--site-root` defaults to `~/infra/docs-site`. Without `--apply`, the command is
a read-only preview. `--prune` is valid only with `--apply`.

## 2. Preconditions and ownership

- `PATH` must be an existing real project directory containing a non-empty,
  real `docs/` directory. Source directory/file symlinks, special files, missing
  docs, empty docs, and source path/directory-component case collisions fail
  closed.
- `SLUG` must match lowercase kebab-case (`[a-z0-9]+(?:-[a-z0-9]+)*`). The
  project/source and site roots must not overlap by normalized lexical or
  physical identity, including case-only aliases.
- The site root must already exist and be real. Existing file or symlink
  destination roots/parents, especially `src/content/docs`, are rejected during
  preview; empty destination directories are allowed but cannot mask an unsafe
  parent. The helper never follows unsafe components.
- Markdown entries become per-file symlinks under
  `src/content/docs/<namespace>`. `.html` and every other regular source file
  become generated copies under `public/<namespace>`.
- Ownership is recorded at `.docs-to-docs-site/<namespace>.json`. The manifest
  contains schema/version, namespace, canonical project/docs realpaths, exact
  destination roots, sorted relative entries, class, size/hash, and Markdown
  symlink targets. It is required before reusing an existing namespace.

## 3. Preview, apply, and prune

Preview reports `additions`, `replacements`, `unchanged`, `stale_owned`,
`errors`, and `warnings` as JSON and performs no writes. Existing namespace
files must be owned by the matching manifest and must match its recorded hash or
symlink target. Unowned files, malformed/mismatched manifests, drift, unsafe
parents, and case collisions are blocking errors.

`--apply` takes an exclusive `.docs-to-docs-site/<namespace>.lock` directory
before loading the prior manifest or analyzing ownership/drift, then holds the
lock through preflight, staging, publication, and smoke check before releasing
it. Preview never creates the lock. Rollback records whether each destination
was removed by this transaction. For normal staged replacements/new
publications, a missing backed-up destination is treated as an external
deletion, so it is preserved and reported as a conflict. Stale-pruned entries
are marked as helper-removed, so missing live paths are restored from backup;
an appearing replacement is removed and restored only when it matches the prior
entry, while drift is preserved and reported. A committed manifest must still
exist and exactly match the candidate before its backup is restored. Conflicts
preserve live edits/deletions and report the conflict. It never materializes
authored Markdown.

Removed source entries are reported as stale and block publication unless
`--apply --prune` is explicit. Prune deletes only stale paths proven by the
matching manifest; it never guesses ownership or removes unowned paths.

## 4. Astro handoff

After a successful publication, run Astro separately from the docs-site root:

```sh
astro check
astro build
```

These are explicit operator steps. Do not install dependencies implicitly, edit
shared config, migrate the site root, or restart a service from this helper or
this skill. If Astro dependencies are absent, stop and resolve that separately.

## 5. Fail-closed policy and common mistakes

Any precondition, ownership, collision, drift, staging, or post-publication
verification error returns non-zero and leaves live outputs unchanged whenever
possible. Inspect the JSON before retrying.

| Mistake                                        | Safe response                                                     |
| ---------------------------------------------- | ----------------------------------------------------------------- |
| Copying Markdown into `src/content/docs`       | Stop; it must remain a symlink to the source.                     |
| Reusing a namespace without its exact manifest | Stop; do not reconstruct ownership from filenames or bytes.       |
| Overwriting a locally edited output            | Stop; drift is a collision, not a replacement approval.           |
| Running `--prune` alone                        | Stop; use explicit `--apply --prune` after reviewing stale paths. |
| Putting the site inside the project            | Stop; fix the source/site overlap.                                |
| Assuming a successful copy is an Astro build   | Stop; run the separate `astro check` and `astro build` handoff.   |
