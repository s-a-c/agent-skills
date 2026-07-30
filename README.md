# s-a-c agent-skills

Portable [agent skills](https://agentskills.io) distilled from a personal
`.agents/rules/` set, packaged for the [Vercel `skills`](https://github.com/vercel-labs/skills)
CLI — "npm for agent skills."

Each skill is a `SKILL.md` with YAML frontmatter (`name` + `description`),
installable into OpenCode, Claude Code, Codex, Cursor, and 40+ other agents.

## Install

```bash
# all skills, interactively
npx skills add s-a-c/agent-skills

# specific skills
npx skills add s-a-c/agent-skills --skill s-a-c-git-write-gate --skill s-a-c-bypass-shell-aliases

# list available skills without installing
npx skills add s-a-c/agent-skills --list
```

See the [`skills` CLI docs](https://github.com/vercel-labs/skills) for global
(`-g`), agent-specific (`-a`), and non-interactive (`-y`) options.

## Skills

| Skill | Use when |
|---|---|
| `s-a-c-code-style-router` | choosing a language-specific code-style rule |
| `s-a-c-frontend-king-mode` | frontend/UI work, or `ULTRATHINK` on a design task |
| `s-a-c-javascript-cli-style` | zero-dependency ESM JavaScript CLI projects |
| `s-a-c-debug-confirmation-gate` | before fixing any bug or error |
| `s-a-c-bypass-shell-aliases` | issuing shell commands that must not hang on aliases |
| `s-a-c-doc-tree-prefixes` | structuring a `docs/` tree with path-derived prefixes |
| `s-a-c-doc-format-parity` | keeping Markdown/HTML documentation in parity |
| `s-a-c-software-doc-lifecycle` | turning research or an idea into a software system |
| `s-a-c-git-write-gate` | before any git write operation |
| `s-a-c-scratch-script-safety` | running scratch scripts safely inside the workspace |
| `s-a-c-governed-memory-substrate` | using a governed memory substrate for recall (parameterized) |

## Layout

```
skills/<name>/SKILL.md   # one file per skill
```

This repo is a **portable export**: the canonical always-on rules live
elsewhere; the skills here are generalized to be workspace-agnostic.
Workspace-specific values in `s-a-c-governed-memory-substrate` are placeholders
to fill in on install.

## License

MIT — see [LICENSE](./LICENSE).
