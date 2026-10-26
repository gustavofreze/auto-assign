---
name: python-writing-tests
description: Creates pytest tests for an artifact of this GitHub Action, routing the scope by the layer the target lives in. Use when asked to write, add, or complete tests, raise coverage, close a missing line or branch, harden assertions, add a Spy double, or do TDD with pytest.
---

# Write tests

Creates tests for an existing artifact, routing the scope by the target. This skill COMPLEMENTS
`rules/python-testing.md`: the rule owns the per-file conventions (`# Given`, `# And`, `# When`, `# Then` comments
with one `# When`, the `test_<action>_when_<condition>_then_<outcome>` name, `tests/` mirroring `src/`, hand-written
`Spy` doubles, `@pytest.mark.parametrize` with `ids`, `pytest.raises` by type, and the 100% line and branch gate). This
skill owns the orchestration around them: which scope a target earns, what does NOT get a dedicated test, and the
machinery to reach for only when the target justifies it.

Target: the artifact to test, named in the request (for example `Issue`, `IssuesAssigningHandler`, or `GitHubIssues`).

Start from the simplest test that drives the behavior. Add machinery only when the target earns it: a Test Data
Builder past roughly five construction parameters, one parameterized test for a matrix of inputs, a `Spy` only at a
boundary, and never a dedicated test for what the decision tree rules out.

Class, port, and method names in the examples match the code under `src/` and the spies under `tests/support/spies/`
(`Issues`, `PullRequests`, `Assignees`, `GitHubIssues`, `ActionSettings`, `IssuesSpy`, `RepositorySpy`). Where a name
in `src/` later drifts from an example, the name in `src/` wins and the shape still applies.

## When to use

- Write, add, or complete tests, raise coverage, close a missing line or branch, harden assertions, do TDD.

## When NOT to use

- **Create the artifact under test.** Building the model, handler, or adapter comes first. Route to
  `rules/python-domain.md` for the domain, to `rules/python-architecture.md` and the
  `python-applying-hexagonal-architecture` skill for ports and adapters, and to `test-driven-development` when the
  tests lead the code. This skill takes the artifact as given.
- **Give a dedicated test to what the decision tree forbids** (a value object, enum, command, domain exception, port,
  or driver support type covered through behavior). Walk `references/unit-test-decision-tree.md` first.
- **Test the composition root.** `src/main.py` and `src/dependencies.py` are excluded from coverage and carry no test.
- **Documentation or configuration changes with no behavior to exercise.**

## Rules applied

Load and follow, in this priority:

- `rules/python-testing.md`: the always-on test invariants. This skill does not restate them.
- `rules/python-code-style.md`: the pre-output checklist, typing, naming, keyword arguments, and formatting. It applies
  to every file under `tests/`, support code included.
- `rules/python-architecture.md`: the layers, the error placement table, and the driven adapter conventions that
  decide what a test of each layer asserts.
- `rules/python-domain.md`: the model, value object, enum, and domain exception shapes a domain test drives.

## Scope at a glance

The first match dictates the scope. Full reasoning per target lives in `references/unit-test-decision-tree.md`.

| Target                                                                          | Scope                | Notes                                                                                                                                                                                                                           |
|---------------------------------------------------------------------------------|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Domain model (`Issue`, `PullRequest`) in `src/application/domain/models`        | **unit**             | Drives the public API. Value objects, enums, and domain exceptions are covered through it.                                                                                                                                      |
| Value object, enum, command, domain exception                                   | **none, by default** | Covered through the model, handler, or driver that consumes it. Dedicated test only on the decision-tree escape hatch.                                                                                                          |
| Handler in `src/application/handlers`                                           | **unit**             | Real domain models and `Spy` outbound ports (`IssuesSpy`, `PullRequestsSpy`, `AssigneesSpy`). The combined handler takes all three spies.                                                                                       |
| Console driver in `src/driver/console`                                          | **unit**             | `Spy` inbound ports. Asserts the exit `Code` per exception family and the command handed to the port.                                                                                                                           |
| Driver support (request parsing, `Result`, `Code`, `src/driver/exceptions`)     | **none, dedicated**  | Covered through the console driver test that reaches each branch.                                                                                                                                                               |
| Driven GitHub adapter (`GitHubIssues`, `GitHubPullRequests`, `GitHubAssignees`) | **adapter test**     | The real adapter against a `RepositorySpy` that duck-types the PyGithub `Repository` and its issue, pull request, and user objects. Asserts recorded calls and the translation of `GithubException` into `GitHubRequestFailed`. |
| Environment adapter (`ActionSettings` in `src/driven/environment`)              | **adapter test**     | A plain `dict` handed to `ActionSettings.from_environment(environment=...)`. Asserts the typed values and the `MissingActionInput` failure.                                                                                     |
| Collaborator with its own behavior (records, journal, output, log formatter)    | **unit**             | The real class: over a `RepositorySpy` where it reads the repository, over files under `tmp_path` for `ActionOutput`, over one `LogRecord` per level for `AnnotationFormatter`.                                                 |
| Application collaborator (`RequestedAssignment` in `src/application`)           | **none, dedicated**  | Covered through the handler tests, each of which builds one over its `AssigneesSpy`.                                                                                                                                            |
| Port (`ABC` in `src/application/ports`)                                         | **nothing to test**  | Pure contract, verified from both sides by the adapter test and the consumer test.                                                                                                                                              |
| Composition root (`src/main.py`, `src/dependencies.py`)                         | **excluded**         | Omitted in `.coveragerc`. Declarative wiring, no test.                                                                                                                                                                          |

## Shapes and how-to (read when scaffolding)

- `references/unit-test-decision-tree.md`: the ordered decision tree, the per-target rulings, the worked shapes for a
  model, a handler, the combined handler, and the console driver, the parameterized shape, when a dedicated non-root
  test IS justified, and testing a domain exception through its raising behavior.
- `references/test-data-builder.md`: builder versus inline construction versus a module-level helper, the frozen
  dataclass builder with `with_*` methods returning a new builder, `build()` placement, state shortcuts
  through the real transitions, cover actions and not accessors, and the two worked usages.
- `references/exception-assertion.md`: `pytest.raises` by type, reading carried context and the chained cause off
  `raised.value`, when `match=` is legitimate, and the prohibited message compare, `try` block, and exception built only
  to be inspected.
- `references/boundary-doubles.md`: the `Spy` shapes for outbound and inbound ports, the `RepositorySpy` and its
  PyGithub object spies, recording calls and asserting on them, raising a `GithubException` on demand, typing the seam
  under `mypy --strict`, and a plain `dict` for the environment.
- `references/coverage-closeout.md`: the `make test` read order over `coverage report --show-missing` and `htmlcov/`,
  reading the report rather than the pass lines, and the pass criterion.

## Assembly order

1. **Decide the scope by the target**, using the table above and `references/unit-test-decision-tree.md`.
2. **Before creating a test module, walk the decision tree.** If the target is a value object, enum, command, domain
   exception, or driver support type, drive it through its consumer instead.
3. **Place the module.** `src/a/b/c.py` is tested in `tests/a/b/test_c.py`, each test package with an empty
   `__init__.py`. Builders go under `tests/support/builders/`, spies under `tests/support/spies/`, nowhere else.
4. **Given/When/Then with exactly one `# When`.** Two actions require two tests. A matrix of inputs is one
   `@pytest.mark.parametrize` test with `ids`, never a copy-paste family.
5. **Construct the subject** inline, through a module-level helper, or through a Test Data Builder, per the fixture
   ladder in `rules/python-testing.md` and `references/test-data-builder.md`.
6. **Double only the boundary** (`references/boundary-doubles.md`). Real models, value objects, and commands inside the
   hexagon. A hand-written `Spy` at each outbound port, inbound port, or third-party seam, never `unittest.mock`,
   `MagicMock`, or `patch`.
7. **Assert failures by type** with `pytest.raises` (`references/exception-assertion.md`).
8. **Run `make review` and `make test`, then close coverage from the report** (`references/coverage-closeout.md`).

## Completeness gate

- [ ] Right path: `tests/` mirrors `src/`, module named `test_<module>.py`, support code only under `tests/support/`.
- [ ] Nothing the decision tree forbids got a dedicated test.
- [ ] Each domain model is covered through its public API, with its value objects, enums, and domain exceptions
  exercised through it.
- [ ] Each handler runs real domain models over `Spy` outbound ports, the combined handler over all three of them.
- [ ] The console driver test reaches every exit `Code` arm through a `Spy` inbound port.
- [ ] Each GitHub adapter test asserts the recorded calls and the typed exception a `GithubException` becomes.
- [ ] Every test has one `# When`, no `if`, `for`, `while`, or `try` in its body, and covers an action or an
  invariant, never a getter and never a `_private` attribute.
- [ ] Every double is a hand-written class ending in `Spy`. No `unittest.mock`, `MagicMock`, `patch`, or
  `monkeypatch.setattr`.
- [ ] Failures asserted with `pytest.raises(X)`, never a message substring unless the message is the action output.
- [ ] `make review` reports clean, and `make test` passes with 100% line and branch coverage read from the report.
