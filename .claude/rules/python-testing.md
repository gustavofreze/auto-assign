---
description: pytest conventions, BDD Given/When/Then with one When per test, test naming and paths mirroring src, the hand-written Spy double policy, fixtures and builders, and the 100% line and branch coverage gate.
paths:
  - "tests/**/*.py"
---

# Testing conventions

Framework: **pytest**, with plain `assert` statements and `pytest.raises`. The decision tree for what earns a
dedicated test, the builder template, and the boundary-double shapes live in the `python-writing-tests` skill. This
rule keeps the always-on invariants. Every rule in `rules/python-code-style.md` applies to test code as well.

## Pre-output checklist

1. The body uses `# Given`, `# And`, `# When`, `# Then` comments, with exactly one `# When`. See § Given/When/Then.
2. The test module mirrors its production module: `src/a/b/c.py` is tested in `tests/a/b/test_c.py`. See § Paths and
   names.
3. Test functions are named `test_<action>_when_<condition>_then_<outcome>`. See § Paths and names.
4. Real objects for collaborators inside the hexagon. Doubles appear only at boundaries, are hand-written, and end in
   `Spy`. `unittest.mock`, `MagicMock`, and `patch` are prohibited. See § Doubles.
5. No conditional logic, loops, or `try` inside a test body. A matrix of inputs is one `@pytest.mark.parametrize`
   test. See § Rules.
6. 100% line and branch coverage. A line that cannot be covered is a design problem in production code. See §
   Coverage.

## Given/When/Then

Every test uses `# Given`, `# And`, `# When`, `# Then` comments without exception, each followed by a short phrase in
domain terms.

```python
def test_assign_when_assignees_are_given_then_issue_carries_them() -> None:
    # Given an issue opened by carol without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the issue is assigned to two members
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new().with_assignees(assignees=Logins.from_raw(values=('alice', 'bob'))).build()
    )

    # Then the issue carries both assignees
    assert assigned_issue == Issue(
        number=1,
        author=Login(value='carol'),
        assignees=Logins.from_raw(values=('alice', 'bob'))
    )
```

For an expected exception, the `# Then` names the failure and wraps the `# When` in `pytest.raises`:

```python
def test_assign_when_no_assignee_is_given_and_empty_assignment_is_denied_then_assignees_required_is_raised() -> None:
    # Given an issue without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # Then the assignment fails because no assignee was given
    with pytest.raises(AssigneesRequired):
        # When the issue is assigned to nobody while an empty assignment is denied
        issue.assign(
            assignment=AssignmentBuilder.new()
            .with_assignees(assignees=Logins.empty())
            .with_allow_no_assignees(allow_no_assignees=False)
            .build()
        )
```

Use `# And` for a complementary precondition or check, never two consecutive `# Given`, `# When`, or `# Then`.

## Rules

1. Exactly one `# When` per test. Two actions require two tests. The single exception is a repeated-invocation test
   (idempotence), where the `# When` holds N identical calls captured in numbered variables (`first`, `second`).
2. Test only the public API. Never assert on a `_private` attribute.
3. Never substitute a collaborator inside the hexagon (a model, a value object, a command). Use the real object.
4. No `if`, `for`, `while`, or `try` in a test body.
5. One logical concept per `# Then` block.
6. Tests are independent. No shared mutable state, no module-level fixtures that mutate.
7. A parameterized scenario is one `@pytest.mark.parametrize` test with `ids` naming each case.
8. Exceptions are asserted by type with `pytest.raises(X)`, never by comparing a message substring. Assert a message
   only when the message itself is the contract (the action output).
9. A value consumed once is inlined at its use site. Named intermediates are for values used twice or for the `# When`
   result.

## Paths and names

- `tests/` mirrors `src/`. Each test package carries an empty `__init__.py`.
- The module is `test_<production module>.py`. Test functions are module-level `def test_...() -> None`. A test
  class is used only to group parameterized cases that share a fixture, and is named `Test<Subject>`.
- Function names follow `test_<action>_when_<condition>_then_<outcome>` in `snake_case`:
    - `test_assign_when_actor_assigns_itself_and_self_assignment_is_denied_then_it_is_refused`
    - `test_unassigned_when_repository_has_mixed_records_then_returns_only_unassigned_issues`
- Shared support code lives under `tests/support/`: `builders/` for test data builders and `spies/` for boundary
  doubles. No other home.

## Doubles

Real objects inside the hexagon. A double appears only at a system boundary (the GitHub API, the environment, the
filesystem, the clock). Every double is a hand-written class ending in `Spy` (`RepositorySpy`, `IssuesSpy`), it
implements the port or duck-types the third-party seam it replaces, and it records calls through plain attributes the
test reads. The suffixes `Mock`, `Stub`, `Fake`, and `Dummy` are prohibited, and any class still ending in one is
renamed during any pass over the file. Variable names use the business concept (`repository`, `issues`), never `spy`
or `mock`.

## Fixtures and builders

1. **Inline construction** for one or two trivial values.
2. **A module-level helper function** in the same test module when an instance is reused across tests of that
   module.
3. **A test data builder** under `tests/support/builders/` past roughly five construction parameters, or when the
   instance is reused across modules. Builders are the one place defaults live in test code.
4. pytest fixtures (`@pytest.fixture`) are used for boundary doubles that need setup. Never for domain values.

## Coverage

Line and branch coverage must be 100% (`coverage run --branch`). Composition-root modules (`src/main.py`,
`src/dependencies.py`) are excluded in `.coveragerc`, and nothing else. A line or branch that cannot be covered
signals a design problem in the production code: refactor the code, never exclude it inline.

## Test organization

- `tests/application/domain/`: model behavior through the model's public API.
- `tests/application/handlers/`: handlers with real domain models and `Spy` outbound ports.
- `tests/driven/<technology>/`: the real adapter against a `Spy` of the third-party seam (a PyGithub `Repository`
  stand-in).
- `tests/driver/console/`: the driver with `Spy` inbound ports, asserting the exit code per outcome.
