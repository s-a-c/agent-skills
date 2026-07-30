---
name: s-a-c-doc-tree-prefixes
description: Structure a docs/ tree with unique path-derived numeric prefixes and reserved contents/index navigation pages. Use when creating, updating, or migrating project documentation.
---

# Documentation Tree Prefixes

> **Core rule:** When creating or updating documentation, follow the required structure below. Apply the default style unless the repository documents an explicit style or renderer override.

## 1. Required structure

- Outside an opted-in OKF bundle, the Markdown body begins with a plain, unnumbered H1 title. Do not add an HTML anchor.
- Use ATX headings only (`##`, `###`).
- Number every heading below the H1 hierarchically. The first H2 begins at `1.`; each deeper level appends its own ordinal, for example `## 1. Section`, `### 1.1. Detail`, and `#### 1.1.1. Detail`.

### 1.1. Path-derived prefixes

- The project's `docs/` root has no prefix. Every version-controlled, non-hidden file and folder beneath it must begin with a unique, path-derived numeric prefix. This includes Markdown files, images, diagrams, generated artifacts, vendor material, archives, and R&D content. A repository may exclude specific subdirectories of `docs/` by naming them in an explicit override (§6); excluded trees are invisible to the prefix, navigation, and migration rules.
- A root child starts with one two-digit tail from `01` through `99`. A descendant appends one new two-digit tail to its parent's complete prefix. Do not place separators between inherited tails; place one hyphen between the completed prefix and its descriptive slug.
- Evaluate only the newly appended tail. A folder tail must be divisible by 3 or 5. A file tail must be divisible by neither 3 nor 5. Reserve `00`; do not use it for any entry.
- Keep direct-sibling tails unique. The concatenated prefix is the entry's project-wide identifier and must never repeat.
- Reserve file tail `01` for the folder's contents page and file tail `98` for its semantic index page. No other direct child may use either reserved tail.

```text
docs/
├── 01-contents.md
├── 05-guides/
│   ├── 0501-contents.md
│   ├── 0502-diagram.svg
│   ├── 0503-reference/
│   │   ├── 050301-contents.md
│   │   └── 050398-index.md
│   └── 0598-index.md
└── 98-index.md
```

In this example, `05` and `03` are valid folder tails; `01`, `02`, and `98` are valid file tails. The folder prefix `0503` and file prefix `050398` are unique because each records the route from `docs/` to its target.

### 1.2. Folder navigation

Every documentation folder, including the `docs/` root, must contain both required navigation pages for its complete prefix `P`:

- `P01-contents.md` is the structural contents page. It states the folder's purpose in one or two sentences, lists every direct child except itself in prefix order with relative links, identifies reading order when it matters, and links to the parent folder's contents page when one exists. Link a direct subfolder through that subfolder's contents page. Include direct non-Markdown assets in this list.
- `P98-index.md` is the semantic index and glossary. It contains a curated, alphabetical topic index and glossary for substantive direct-child Markdown pages. Each topic and glossary term links to the relevant heading or subheading; each glossary term also has a concise definition. Link direct subfolders to their own semantic index page. Exclude both structural navigation pages and non-Markdown assets from this page. Write `None` in an empty index or glossary section rather than omitting the section.

For the `docs/` root, `P` is empty, so its required pages are `01-contents.md` and `98-index.md`. For `05-guides/`, they are `0501-contents.md` and `0598-index.md`.

### 1.3. Legacy migration and capacity

- A legacy documentation subtree may remain unchanged. When a substantive content edit or a structural change adds, removes, renames, reorganizes, or materially revises an entry, migrate the smallest enclosing documentation folder and all of its descendants to this structure. Repair ancestor navigation links that point into the migrated subtree.
- An isolated typo or link repair does not trigger migration.
- When a folder has no valid unused two-digit tail for a required child, introduce another documentation folder to split the branch. Do not widen tails or reuse a tail.

## 2. Open Knowledge Format bundles

- The path-derived prefix and navigation requirements above govern `docs/` and its descendants. An OKF bundle must live outside `docs/`; do not use OKF to waive this contract within that tree.
- A directory outside `docs/` opts into strict Google Cloud Open Knowledge Format (OKF) v0.1 when it contains a hidden `.okf-bundle` marker. The marker defines the bundle root and all descendants.
- Every Markdown file in an opted-in bundle is an OKF concept document unless it is the reserved `index.md` or `log.md`. A concept document begins with parseable YAML frontmatter containing a non-empty `type` field, followed by a standard Markdown body.
- `index.md` and `log.md` use their respective OKF reserved-file structures and must not be treated as concept documents. Other Markdown files, including README-style files, remain concept documents and require `type`.

## 3. Default style

- **Collapsible TOC:** When targeting GitHub Markdown, add this TOC immediately after the H1. List every H2 through H4 heading as a nested Markdown link list using the GitHub-compatible anchors defined in §5. Skip it when the platform generates its own TOC.

  ```md
  <details>
    <summary style="font-size: 1.25em; font-weight: bold; margin: 0.83em 0; cursor: pointer;">
      Expand for Table of Contents
    </summary>

    - [1. Section](#1--section)
      - [1.1. Detail](#11--detail)

  </details>

  ---
  ```

- **Emoji in headings:** Include a relevant emoji after the numeric prefix (`## 1. Section`). Omit it when a repository override, accessibility concern, or formal publication target forbids it.
- **Navigation footer:** Add `[← Previous](prev.md) | [↑ Top](#title) | [Next →](next.md)` only when a repository opts in.

## 4. Visual and accessibility

All diagrams, images, and rendered visuals must meet WCAG 2.1 AA:

- Provide sufficient contrast, avoid color-only meaning, and add alt text or text summaries for every visual.
- Every Mermaid block begins with YAML frontmatter that selects the configurable `base` theme and sets `themeVariables.fontSize` to `16px`; this establishes a minimum rendered label size. Set node `fill`, `stroke`, and text `color` to high-contrast values. Keep diagrams focused; split large diagrams instead of shrinking labels.

  ```mermaid
  ---
  config:
    theme: base
    themeVariables:
      fontSize: 16px
  ---
  flowchart TD
    start["Start"] --> finish["Finish"]
  ```

- Use a dark background (`#1e1e1e`) with light text (`#d4d4d4`) for code blocks in colored containers.
- Wrap Mermaid and diagram label strings in double quotes to avoid parser ambiguity.

## 5. Links

Internal links and TOCs use GitHub-compatible anchors unless the repository documents another renderer. Generate anchors by lowercasing, replacing spaces with hyphens, and removing punctuation, including emoji. Keep emoji in the visible heading and TOC label, but omit it from the generated fragment; always verify the rendered link.

When fixing a broken link, create or correct the missing content when possible. Delete the link only when its target is obsolete or intentionally removed.

## 6. Overrides

Repository-specific rules may override only default presentation choices and renderer-specific link conventions when they are explicit and discoverable. They may not waive the required prefix grammar, reserved navigation pages, tracked-entry coverage, legacy migration rules, or opted-in OKF requirements.

## See Also

- `s-a-c-doc-format-parity` — keeps Markdown and HTML renderings in parity.
- `s-a-c-software-doc-lifecycle` — decision flow that fills this tree.
