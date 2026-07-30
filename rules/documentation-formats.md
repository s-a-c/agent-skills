---
description: Shared Markdown and HTML documentation contract — apply when creating or updating documentation
alwaysApply: true
---

# Shared Documentation Formats

Always-on wrapper for the **`s-a-c-doc-format-parity`** skill. This rule fires
every turn; when its trigger applies, invoke that skill for the full gate body.
The skill is the single source of the body — this file only enforces always-on
routing.

**Prerequisite:** install the skill first
(`npx skills add s-a-c/agent-skills --skill s-a-c-doc-format-parity`).
**Adopt:** copy this file into your agent's always-on rules location
(`.cursor/rules/`, `~/.config/agents/rules/`, `.clinerules/`, …) and adapt the
frontmatter to your agent's rule format. `npx skills add` installs skills, not
these rules.
