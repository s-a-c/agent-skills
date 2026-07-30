---
name: s-a-c-git-write-gate
description: Check the project agent-config before any git write operation and skip it when auto-commit is disabled. Use before any git add, commit, push, pull, merge, tag, branch delete, rebase, or reset.
---

# Git Write Gate

> **Core rule:** Before ANY git write operation, read the project agent-config file (e.g. `.agents/config.yml`) — if `auto_commit: false`, skip the operation and print "Skipping git operation (auto_commit: false)."

> **Gate (must):** Before running ANY git write operation — `git add`, `git commit`,
> `git push`, `git pull`, `git merge`, `git tag`, `git branch -d`, `git branch -D`,
> `git worktree remove`, `git rebase`, `git cherry-pick`, `git reset --hard` —
> you MUST read the project agent-config file (for example `.agents/config.yml`)
> and check the `auto_commit` setting.
>
> If `auto_commit: false`:
> - DO NOT run the operation
> - Print exactly: "Skipping git operation (auto_commit: false)."
> - Continue with the rest of the task (non-git steps still execute)
>
> If `auto_commit: true` (or key is absent): proceed normally.

This applies everywhere — inside skills, workflows, and any ad-hoc actions.
No exceptions.

## Config location

The gate reads the project's agent-config file. The conventional name is
`.agents/config.yml`; a repository may document a different path or key name in
its `AGENTS.md`. When the file or key is absent, treat `auto_commit` as `true`.

## Always Allowed (read-only)

These operations are never blocked:
- `git status`, `git log`, `git diff`, `git show`
- `git worktree add`, `git worktree list`
- `git checkout <branch>` (navigation only)
