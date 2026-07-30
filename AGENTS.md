# AGENTS.md — s-a-c/agent-skills

This repository is a **portable governance pack** for the Vercel `skills` CLI
(`npx skills add s-a-c/agent-skills`): opt-in **skills** (`skills/`), where each
**gate** skill additionally carries a co-located **always-on wrapper**
(`skills/<gate>/rules/<rule-name>.md`). It is an EXPORT: the skills are
generalized to be workspace-agnostic; persona/meta rules stay workspace-local.

## Conventions

- One skill per folder: `skills/<name>/SKILL.md`.
- Every skill `name` is prefixed `s-a-c-` and is trigger-descriptive
  (lowercase, hyphens only).
- `SKILL.md` frontmatter: `name` + `description` (trigger-based "use when…").
  Optional `metadata.internal: true` for work-in-progress. No other fields.
- Skills are PORTABLE: no hardcoded machine paths, hostnames, or workspace
  identifiers. Workspace-specific values become placeholders (see
  `s-a-c-governed-memory-substrate`).
- `HARD-GATE` rule blocks become a top-of-body `> **Gate (must):**` callout.
- Cross-references use sibling skill names, not source rule filenames.

## Always-on gate wrappers (co-located)

Some skills are hard gates that must fire every turn (git-write, debug-confirm,
scratch-script safety, shell-alias bypass, doc-tree, doc-format, doc-lifecycle).
An opt-in skill alone cannot guarantee that, so each gate skill ships a thin
always-on wrapper under its own `rules/` subdir —
`skills/<gate>/rules/<rule-name>.md` — with `alwaysApply: true` and a body that
only routes to the matching `s-a-c-*` skill.

- The skill (`SKILL.md`) is the single source of the gate body; the co-located
  `rules/<rule-name>.md` only enforces always-on routing.
- `npx skills add --skill <gate>` fetches **both** (the skill folder is copied
  whole). The wrapper is NOT enforced by installation — `npx skills` installs
  opt-in skills, not always-on rules. To enforce it, copy the
  `rules/<rule-name>.md` into your agent's always-on rules location
  (`~/.config/agents/rules/`, `.cursor/rules/*.mdc`, `.clinerules/`, …); the
  filename is already the conventional rule name, so no rename is needed. To stop
  enforcement, delete that copy. Each wrapper carries the exact `cp`/`curl`
  one-liner and its prerequisite skill.
- Capability skills (no gate) have no `rules/` — naturally "without rule".

## Verifying

```bash
npx skills add ./ --list        # discover all skills from a checkout
```

Every `SKILL.md` must carry valid `name` + `description` frontmatter, and every
`name` must be unique.

## Scope

Trigger-shaped / capability **skills** (`skills/<name>/SKILL.md`), where gate
skills additionally carry a co-located **always-on wrapper**
(`skills/<gate>/rules/<rule-name>.md`). Always-on persona and global policies
(communication style, language matching, etc.) are intentionally NOT packaged —
opt-in skills would weaken their always-applies nature, and they are not gates.
