---
name: s-a-c-code-style-router
description: Route to the right language-specific code-style rule before applying any code style conventions. Use when a code change needs style guidance and you must pick which convention set applies.
---

# Code Style Router

Use this skill before applying code style conventions. It decides which
language-specific rule to read.

Do not apply a language style globally. Use the nearest project instructions
first, then the matching style below.

## Routing

- **JavaScript CLI projects:** use `s-a-c-javascript-cli-style` when the project is
  plain ESM JavaScript, zero-dependency, and CLI-oriented.
- **TypeScript projects:** use the nearest project `AGENTS.md`, package tooling, or
  an installed TypeScript skill. No global TypeScript style is defined here.
- **PHP or Laravel projects:** use the nearest project `AGENTS.md` and Laravel/PHP
  skills. Do not apply JavaScript CLI conventions.
- **Markdown and documentation:** use `s-a-c-doc-tree-prefixes`, not a code style
  skill.
- **Frontend and UI work:** use `s-a-c-frontend-king-mode` for UI persona, library
  discipline, and response format. Use a `frontend-design` skill when its trigger
  applies.

## Adding A Language Rule

When a convention is truly reusable across repositories, add a focused style skill
scoped by language and project type — for example a `s-a-c-php-laravel-style`
peer to `s-a-c-javascript-cli-style`. Keep each one scoped to one language and
project type.

## See Also

- `s-a-c-javascript-cli-style`
- `s-a-c-frontend-king-mode`
- `s-a-c-doc-tree-prefixes`
