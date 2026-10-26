# auto-assign

Python GitHub Action. Hexagonal architecture (ports and adapters) with commands and handlers. It assigns open issues
and pull requests to the configured assignees.

Those two lines are the part of this file that belongs to this project. Everything below the divider is the portable
Python toolkit, and adopting it elsewhere is `cp -r .claude/` plus this file, then rewriting those two lines.

---

## Reference-first approach

Read the relevant rule files and the existing code before generating anything. Match the established pattern. Do not
work from memory.

- All Python code: `rules/python-code-style.md` (pre-output checklist, typing, immutability, naming, docstrings,
  exceptions, imports, suppressions).
- All Python code under `src/`: `rules/python-design-principles.md` (precedence ladder, MUST and SHOULD binding,
  shared-code homes).
- All Python code under `src/`: `rules/python-architecture.md` (inward-only dependency rule, layer contract, commands
  and handlers, error placement, driven adapter naming, composition root).
- Domain layer (`src/application/domain/`): `rules/python-domain.md` (models, value objects, enums, domain
  exceptions, import whitelist).
- All tests (`tests/`): `rules/python-testing.md` (pytest, Given/When/Then, naming, Spy doubles, coverage).
- Workflows and `action.yml`: `rules/github-workflows.md`.
- `Dockerfile`: `rules/docker-images.md`.

## Stack

Refer to `pyproject.toml` for the Python version and every dependency. Static analysis is pylint (`.pylintrc`) and
mypy in strict mode. Tests run under pytest with coverage (`.coveragerc`).

## Project layout

```
src/
├── application/
│   ├── domain/{models,exceptions}/   # framework-free core
│   ├── commands/                     # one frozen dataclass per use-case intent
│   ├── handlers/                     # one handler per inbound port
│   ├── ports/{inbound,outbound}/     # ABC contracts
│   └── requested_assignment.py       # command primitives to Assignment, shared by every handler
├── driver/console/                   # driving adapter: action inputs to command, outcome to exit code
├── driven/<technology>/              # driven adapters: github, environment
├── dependencies.py                   # composition root (dependency_injector container)
└── main.py                           # process entry point
tests/                                 # mirrors src/, plus tests/support/{builders,spies}/
```

The layer contract is owned by `rules/python-architecture.md`. Read it before creating any module under `src/`.

## Commands

Every Python command runs inside Docker through the `Makefile`. Run `make help` for the actual list. Verify a target
exists before invoking it, and where one is missing, use the nearest equivalent and report the gap.

- `make configure`: install dependencies into the in-project virtualenv.
- `make test`: run the suite with coverage.
- `make review`: run static analysis.
- `make run`: run the action locally against `.env.development`.
- `make smoke`: build the shipped image and run it against a real sandbox repository, with the token in `.env.local`.
  It writes to that repository, so run it only when asked.
- `make publish`: build and push the action image to the registry. `release.yml` runs it on a published release.
  Never run it locally unless asked, because it publishes.

## Post-change validation

After any code change, run `make review` and `make test`. If either fails, iterate on the fix while respecting every
rule until both pass. Never deliver code that breaks lint, types, or tests.

## Dependency policy

NEVER install or upgrade to a package version released less than 7 days ago. The cooldown applies to every
dependency manager in this repository (`poetry`, `pip`, GitHub Actions pins). Packages and actions the repository
owner maintains (the owner segment of `git remote get-url origin`) are exempt, because the owner already knows what
the release contains. Before pinning any other version, verify its release date against `today - 7 days`. If the
latest is too recent, fall back to the previous version that satisfies the cooldown and flag the fallback.

## Global defaults

These apply across every file in the repository, regardless of path.

- **Prose punctuation.** Do not use `;`, an em-dash, an en-dash, or ` -- ` as clause separators in Markdown, Python
  comments, or docstrings. Use two sentences, a comma, a colon, or parentheses. Hyphens in compound words, fenced
  code, and Markdown tables are exempt. A hook enforces it.
- **No inline analyzer suppression.** `# pylint: disable`, `# type: ignore`, `# noqa`, and `# pragma: no cover` are
  prohibited in every Python file. The suppression channels are `.pylintrc`, `pyproject.toml` (`[tool.mypy]`), and
  `.coveragerc`, each entry scoped and justified. A hook enforces it.
- **Secrets in versioned files.** Never commit real secret values. Every tracked file carries placeholders or
  local-only defaults, `.env.development` included. Real tokens live only in a git-ignored `.env.local` or in the
  repository secrets.
- **American English** in identifiers, comments, docstrings, messages, and documentation.

## Conventions

Rules (`.claude/rules/*.md`) are persistent invariants injected when you read a file matching their `paths:` glob.
Skills (`.claude/skills/<name>/SKILL.md`) are intent-triggered workflows and references. A rule is an invariant (what
must always hold), a skill is a workflow or a teaching reference (how to build within those invariants), and each
concern has a single owner. A skill defers to the rules covering the files it touches, it never overrides them.
Stack-specific artifacts carry the `python-` prefix. Stack-neutral ones (`github-workflows`, `docker-images`,
`writing-commit-messages`) carry none.

No file under `.claude/` may carry an organization name, a registry host, a sibling directory path, or a public domain.
That keeps the tree portable.

### Read the rule before creating a new file

Path-scoped rules are injected on **Read** but not on **Write** of a new file. Before creating any file under a glob a
rule covers, explicitly read the matching `.claude/rules/*.md`.

### Hooks

`.claude/hooks/` holds stdlib-only Python checks wired in `.claude/settings.json`: the `.env` guard (PreToolUse), the
prose punctuation check, the hexagonal layer check, and the inline suppression check (PostToolUse). A hook exit code
`2` feeds its findings back for correction. Their behavior tests run with
`python3 -B .claude/hooks/tests/test_hooks.py`.

### Authority and conflict resolution

Rules and skills are the default authority for every task. On business behavior, the action contract (`action.yml`
and `README.md`) wins: never invent behavior the contract does not state, stop and ask. If two rules overlap, favor the
more specific one. Flag any real contradiction before deviating from either.

## Commits

Commit messages follow the `writing-commit-messages` skill: Conventional Commits, no scope, English, imperative,
trailing period, no trailers and no attribution of any kind.
