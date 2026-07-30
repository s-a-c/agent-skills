# AGENTS.md — s-a-c/agent-skills

This repository is a **portable governance pack** for the Vercel `skills` CLI
(`npx skills add s-a-c/agent-skills`): opt-in **skills** (`skills/`) plus
**always-on gate-wrapper rule templates** (`rules/`). It is an EXPORT: the
skills are generalized to be workspace-agnostic; persona/meta rules stay
workspace-local.

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

## Rules — always-on gate wrappers (`rules/`)

Some skills are hard gates that must fire every turn (git-write, debug-confirm,
scratch-script safety, shell-alias bypass, doc-tree, doc-format, doc-lifecycle).
An opt-in skill alone cannot guarantee that, so `rules/` ships one thin
always-on wrapper per gate skill — `alwaysApply: true` with a body that only
routes to the matching `s-a-c-*` skill.

- The skill is the single source of the gate body; the rule only enforces
  always-on routing.
- `npx skills add` installs the **skills**, not these rules (the skills CLI has
  no always-on-rule install mechanism). To adopt a gate wrapper, copy its file
  into your agent's always-on rules location (`.cursor/rules/`,
  `~/.config/agents/rules/`, `.clinerules/`, …), install the prerequisite skill,
  and adapt the frontmatter to your agent's rule format.
- Each `rules/<name>.md` names its prerequisite skill in its body.

## Verifying

```bash
npx skills add ./ --list        # discover all skills from a checkout
```

Every `SKILL.md` must carry valid `name` + `description` frontmatter, and every
`name` must be unique.

## Scope

Trigger-shaped / capability **skills** (`skills/`) plus **always-on gate-wrapper
rule templates** (`rules/`). Always-on persona and global policies
(communication style, language matching, etc.) are intentionally NOT packaged —
opt-in skills would weaken their always-applies nature, and they are not gates.
