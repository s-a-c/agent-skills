---
name: s-a-c-javascript-cli-style
description: Code style for zero-dependency ESM JavaScript CLI projects. Use when the project is plain ESM JavaScript under bin/ with no TypeScript build pipeline and no runtime npm dependencies.
---

# JavaScript CLI Style

Use this rule only for plain JavaScript CLI projects that are ESM,
zero-dependency, and not TypeScript.

## Scope

Apply this rule when the nearest project instructions or package metadata show:

- `"type": "module"` in `package.json`
- CLI entry points under `bin/`
- No TypeScript build pipeline
- No runtime npm dependencies

Do not apply this rule to TypeScript, frontend apps, Laravel/PHP projects, or
documentation-only work.

## Naming

- Variables and functions: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Files and folders: `kebab-case`
- Avoid PascalCase unless the local project introduces classes or components.

## File Structure

- `bin/` contains CLI entry points only.
- `scripts/` contains build and utility scripts that are not shipped.
- `template/` contains files copied into a user's `.agents/` on init.
- `.agents/` contains agent rules, skills, and workflows; keep it out of
  package `files[]`.
- Keep one responsibility per file. Do not add barrel files unless the project
  already uses them.

## Formatting

- Indentation: 2 spaces.
- Quotes: single quotes.
- Semicolons: always.
- Max line length: 100 characters as a soft limit.
- Trailing commas: yes for ES2017+ syntax.

## Patterns

- Use ESM `import` and `export`; do not use `require()`.
- Prefer `async` and `await` over `.then()` chains.
- For CLI errors, use `console.error()` and `process.exit(1)`.
- Use Node.js `fs`; synchronous filesystem calls are acceptable for simple CLI
  scripts.
- In ESM, derive `__dirname` with
  `path.dirname(fileURLToPath(import.meta.url))`.
- Order imports as Node built-ins, npm packages, then local files.

## Comments

- Add usage comments where they clarify non-obvious CLI behavior.
- Do not add comments that merely restate code.
- Avoid JSDoc unless the function is exported as a public API.

## Avoid

- No TypeScript in projects that intentionally use plain JavaScript.
- No new runtime dependencies unless explicitly approved.
- No dynamic `import()` unless the project needs lazy loading or optional modules.
- No guessed types or placeholders; fail loudly with a clear message when path or
  runtime assumptions are unclear.

## See Also

- `s-a-c-code-style-router` — routes a project to this style.
