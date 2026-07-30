---
description: CRITICAL — Scratch scripts must run inside workspace (.agents/tmp/), NEVER in /tmp/
alwaysApply: true
---

# Scratch Scripts Policy

Always-on wrapper for the **`s-a-c-scratch-script-safety`** skill. This rule
fires every turn; when its trigger applies, invoke that skill for the full gate
body. The skill is the single source of the body — this file only enforces
always-on routing.

**Prerequisite:** install the skill first
(`npx skills add s-a-c/agent-skills --skill s-a-c-scratch-script-safety`).
**Adopt:** copy this file into your agent's always-on rules location
(`.cursor/rules/`, `~/.config/agents/rules/`, `.clinerules/`, …) and adapt the
frontmatter to your agent's rule format. `npx skills add` installs skills, not
these rules.
