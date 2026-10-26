# Coverage close-out procedure (read from the report)

Read this when verifying that a suite reaches full coverage before declaring testing work done. None of it is a
per-file invariant, so it is not path-injected. The gate itself (100% line and branch coverage, the composition root as
the only exclusion, and refactoring the code rather than excluding a line) lives in `rules/python-testing.md` §
Coverage. This file holds the report-reading procedure that backs that gate.

## Verify from the report, never from the pass lines

The `make test` output is not a source of truth. The pytest progress dots, the `N passed in 0.42s` summary, and a
green exit say that the tests ran and passed. They say nothing about which lines and branches no test reaches. Read
the coverage report.

`make test` runs the suite under `coverage run`, then prints `coverage report` and writes the annotated HTML under
`htmlcov/`. The `.coverage` data file and `htmlcov/` are gitignored, so on a fresh clone neither exists until
`make test` has run. If they are missing or older than the last change, run `make test` first.

| Artifact                         | What it is                                                                                                      | Read it to                                                  |
|----------------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| `.coverage`                      | The raw data file. Machine input.                                                                               | Feed `coverage report` and `coverage html`. Never by eye.   |
| `coverage report --show-missing` | One row per module with `Stmts`, `Miss`, `Branch`, `BrPart`, `Cover`, and `Missing`, then the `TOTAL` row.      | Read the gate and locate each missing line and branch.      |
| `htmlcov/index.html`             | The same table, linking to each module annotated line by line. Missed lines in red, partial branches in yellow. | See the exact branch a test still misses.                   |

In the `Missing` column a bare number is a line no test ran, and `14->17` is a branch from line 14 to line 17 that no
test took. `14->exit` is a branch out of the function that no test took, typically the fall-through past a guard
clause.

## Branch coverage must be on

The gate is line **and** branch coverage. The report must carry the `Branch` and `BrPart` columns, which appear only
when the data was collected with branch measurement (`branch = True` in `.coveragerc`, or `coverage run --branch`). A
report without those columns is not evidence for the gate, even at 100%.

The only omitted production modules are the composition root: `src/main.py` and `src/dependencies.py`. Any other `omit`
entry, and any `exclude_lines` pattern that hides production lines, is an exclusion the rule does not admit. Report it
as a finding, never widen it.

## Read order (keep context small)

Pull the minimum into context. Escalate only when the cheaper read is not green.

1. **The `TOTAL` row first.** It is the last line `make test` prints from `coverage report`. Smallest signal and the
   gate: `Cover` at `100%`, with `Miss` and `BrPart` at `0`. If it holds, stop here.
2. **`coverage report --show-missing --skip-covered` when the total is short.** It lists only the modules below 100%,
   each with its `Missing` lines and branch arcs. Read those rows, never the whole table when the filtered one is
   enough.
3. **The module page under `htmlcov/` for each flagged module.** Open only the pages the filtered report named, and
   read the red lines and the yellow partial branches. Those are the precise statements and arcs no test drives yet.
   `make show-reports` opens the index in a browser.

Run the second step in the same environment `make test` uses. When no make target exposes it, read `htmlcov/`
instead and report the missing target as a tooling finding. Never skip the verification for want of a target.

## Closing a gap

Map each missing line or arc to the behavior that reaches it, then to the test scope that owns that behavior
(`references/unit-test-decision-tree.md`):

- A missed arm of the console driver's exit-code mapping closes with a driver scenario whose inbound `Spy` raises an
  exception of that family. Never a test of the mapping in isolation.
- A missed `except GithubException` in a GitHub adapter closes with a `RepositorySpy(..., failure=GithubException(...))`
  scenario.
- A missed guard in a model closes with the input that trips it, driven through the model's public method.
- A missed promotion in `ActionSettings` closes with a scenario whose `environment` `dict` carries the raw value.

## Full coverage of behavior is the gate

Coverage is a lagging indicator of behavior tested, not a number to farm. Every line and branch must be driven by a
test that would fail if the behavior broke. Closing a red line with a test that asserts nothing, or with one that
constructs a value only to read its attribute back, moves the number without covering behavior, and
`rules/python-testing.md` forbids it.

When a line or branch genuinely cannot be reached by any meaningful input, that is a design signal: delete the dead
branch, collapse the impossible path, or move the guard into `__post_init__` so the invalid state is unrepresentable.
`# pragma: no cover` and a new `.coveragerc` exclusion are both prohibited (`rules/python-code-style.md` § Analyzer
suppressions). See the `python-applying-design-principles` skill for the refactor.

## Mutation testing (optional, a SHOULD, not a gate)

Coverage proves a line ran. It does not prove an assertion would fail if the line's logic were wrong. Mutation testing
closes that gap by changing operators and conditions and rerunning the suite per mutant. No mutation tool is wired into
`make test` here, and none blocks a change.

Reach for one ad hoc when hardening a model invariant or the exit-code mapping. `mutmut` and `cosmic-ray` both run a
pytest suite per mutant and report the survivors. Treat a surviving mutant the way you treat a red line: strengthen the
assertion that should have caught it, or delete the logic if it was never load-bearing. Do not fabricate a make target
or a report path around these tools.

## Coming from the Go and PHP procedures

| Elsewhere                                                   | Here                                                               |
|-------------------------------------------------------------|--------------------------------------------------------------------|
| `go tool cover -func ... \| tail -1`, `coverage.txt` totals | the `TOTAL` row of `coverage report`                               |
| sub-100% rows of `-func`, per-line `coverage.txt` entries   | `coverage report --show-missing --skip-covered`                    |
| `coverage.html` red spans                                   | the module page under `htmlcov/`, red lines and yellow partials    |
| Infection summary as a gate                                 | none, mutation testing is optional and ungated                     |
