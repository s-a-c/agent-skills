# AGENTS.md — s-a-c/agent-skills

This repository is a **portable distribution of agent skills** for the Vercel
`skills` CLI (`npx skills add s-a-c/agent-skills`). It is an EXPORT: the
canonical always-on rules live elsewhere; the skills here are generalized to be
workspace-agnostic.

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

## Verifying

```bash
npx skills add ./ --list        # discover all skills from a checkout
```

Every `SKILL.md` must carry valid `name` + `description` frontmatter, and every
`name` must be unique.

## Scope

Trigger-shaped / capability skills only. Always-on persona and global policies
are intentionally NOT packaged here — they belong as always-on rules, not
opt-in skills.
