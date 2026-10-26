# Test scope decision tree (read before creating a test module)

Read this while deciding whether a target gets a dedicated test and what that test drives. None of it is a per-file
invariant, so it is not path-injected. The kept invariants live in `rules/python-testing.md` and the
`python-writing-tests` skill. This reference holds the decision support and the worked shapes.

Unit tests drive behavior through the type that owns it. By default, do NOT create a dedicated test module for a value
object, enum, command, domain exception, port, or driver support type. Coverage arrives through the domain model test,
the handler test, the console driver test, or the driven adapter test that runs the code path.

## Contents

- At-a-glance verdict table
- Decision tree
- Details per target
- Worked shapes
- When a dedicated non-root test IS justified
- Testing a domain exception through the raising behavior

## At-a-glance verdict table

First matching row wins.

| Target                                                     | Location                                      | Verdict                                                                |
|------------------------------------------------------------|-----------------------------------------------|------------------------------------------------------------------------|
| Composition root                                           | `src/main.py`, `src/dependencies.py`          | No test. Omitted in `.coveragerc`                                      |
| Inbound or outbound port (`ABC`)                           | `src/application/ports/{inbound,outbound}`    | Nothing to test, pure contract                                         |
| Console driver                                             | `src/driver/console`                          | Driver test with `Spy` inbound ports, exit `Code` per family           |
| Log formatter (`AnnotationFormatter`)                      | `src/driver/console`                          | Dedicated test, one `LogRecord` per level                              |
| Driver support (request, `Result`, `Code`, option parsing) | `src/driver/console`, `src/driver/exceptions` | No dedicated test, covered by the driver test                          |
| GitHub adapter                                             | `src/driven/github`                           | Adapter test against `RepositorySpy`                                   |
| GitHub collaborator with behavior (records, journal)       | `src/driven/github`                           | Collaborator test, real class, `RepositorySpy` where it reads          |
| Translation shared by GitHub adapters                      | `src/driven/github`                           | No dedicated test, covered by the adapter tests that use it            |
| Environment adapter (`ActionSettings`)                     | `src/driven/environment`                      | Adapter test handing a plain `dict` to `from_environment`              |
| Action output (`ActionOutput`)                             | `src/driven/environment`                      | Adapter test writing into files under pytest `tmp_path`                |
| Handler                                                    | `src/application/handlers`                    | Handler test, real domain, `Spy` outbound ports                        |
| Application collaborator (`RequestedAssignment`)           | `src/application`                             | No dedicated test, covered by the handler tests                        |
| Command                                                    | `src/application/commands`                    | No test, covered by the handler and driver tests                       |
| Value object, enum, domain exception                       | `src/application/domain`                      | No dedicated test, covered through the model (narrow exceptions below) |
| Domain model (`Issue`, `PullRequest`)                      | `src/application/domain/models`               | Dedicated unit test                                                    |

## Decision tree

Before writing a new test module, walk these questions in order. The first match dictates the answer.

1. **Is the target `src/main.py` or under `src/dependencies.py`?**
    - **NO TEST.** The composition root is declarative wiring over `dependency_injector` and is omitted in
      `.coveragerc`. It is the only exclusion the coverage gate admits.
2. **Is the target an `ABC` under `src/application/ports/`?**
    - **NOTHING TO TEST.** A port carries no behavior. The adapter test proves an implementation honors it, and the
      handler or driver test proves the consumer drives it.
3. **Is the target under `src/driver/`?**
    - If it is the console driver class, write the **driver test** at the mirrored `tests/driver/console/` path, with a
      `Spy` in place of each inbound port. The driver test asserts the exit `Code` for each exception family and the
      command the driver handed to the port.
    - Otherwise, NO dedicated test. It is driver support: the request the inputs are read into, the assignment option
      parsing, `Result`, `Code`, and the exceptions under `src/driver/exceptions`. The driver test that reaches each
      branch covers them. See "Driver support" below. The exception is `AnnotationFormatter`: only the composition
      root installs it, so its test formats one `logging.LogRecord` per level.
4. **Is the target under `src/driven/github/`?**
    - If it is an adapter implementing an outbound port (`GitHubIssues`, `GitHubPullRequests`, `GitHubAssignees`), write
      the **adapter test** at the mirrored `tests/driven/github/` path, running the real adapter against a
      `RepositorySpy` (`references/boundary-doubles.md`).
    - If it is a collaborator with observable behavior of its own (`GitHubIssueRecords` choosing the listing call,
      `AssignmentJournal` and `JournalEntry` producing the action outputs and summary rows), write its test at the
      mirrored path against the real class, over a `RepositorySpy` where it reads the repository.
    - Otherwise, NO dedicated test. A translation used by every GitHub adapter (PyGithub record to domain model) is
      covered through the adapter tests that run it.
5. **Is the target under `src/driven/environment/`?**
    - Write the **adapter test** at the mirrored `tests/driven/environment/` path, handing the action inputs to
      `ActionSettings.from_environment(environment=...)` as a plain `dict` and dropping a key to remove one. See
      "Environment adapter" below for why this differs from a tautology. `TriggeringEvent` gets its own test the same
      way, and `ActionOutput` writes into files under pytest `tmp_path`, because the composition root is their only
      consumer.
6. **Is the target under `src/application/handlers/`?**
    - Write the **handler test** at the mirrored `tests/application/handlers/` path, with real domain models and a `Spy`
      in place of each outbound port.
    - The handler that assigns pull requests and issues in one run is no exception. It depends on the `Issues`,
      `PullRequests`, and `Assignees` outbound ports directly, never on another handler, so its test seeds all three
      spies.
    - `RequestedAssignment` at the `src/application/` root gets no dedicated test. Every handler builds one over the
      `AssigneesSpy` it receives, so the handler tests run it.
7. **Is the target under `src/application/commands/`?**
    - **NO TEST.** A command is a frozen dataclass naming one intent. The driver test proves the driver builds it, the
      handler test proves the handler acts on it.
8. **Is the target a domain type other than a model?** (value object, enum, domain exception)
    - **NO dedicated test by default.** Coverage arrives through the model that consumes it. See "Domain types covered
      through the model" for the narrow exceptions.
9. **The target is a domain model, a handler, the console driver, or a driven adapter.** Write the test.

## Details per target

**Domain models** (`Issue`, `PullRequest`). Tested through the public API only: each transition
(`assign(assignment=...)`) that returns a new instance, or `self` when `assignment.excludes(author=..., draft=...)`,
and through it the `Assignment` value object in `models/commons` whose `granted_assignees(author=...)` raises
`AssigneesRequired` or `SelfAssignmentNotAllowed`. A test asserts
the new instance a transition returns, or the domain exception it raises, never the attributes a constructor was just
handed.

**Handlers**. Thin orchestrators whose behavior is the conversation between real models and the outbound ports. Seed
each outbound `Spy` with what the port returns, run `handle(command=...)`, and assert what the `Spy` recorded (the
models handed back to the port) and the domain exception that escapes when a model refuses. A handler test never
asserts on a model's internals: the model has its own test.

**Combined handler** (`PullRequestsAndIssuesAssigningHandler`, which assigns pull requests and issues in one run). It
talks to the outbound ports directly, so its test hands it `IssuesSpy`, `PullRequestsSpy`, and `AssigneesSpy` and
asserts what each recorded, including that the repository was asked about the assignees once for both kinds. A
handler never invokes another handler, so no inbound `Spy` appears in a handler test.

**Driver support**. Everything under `src/driver/` that is not the console driver class. The exit-code mapping arms,
the option parsing, and the `Result` are covered by the driver tests that reach each branch. A dedicated test that
only asserts a mapping round trip in isolation duplicates coverage and bypasses the real call path. An exit-code arm
no driver test reaches is uncovered code, closed by adding the missing driver scenario: make the inbound `Spy` raise an
exception of that family and assert the `Code`.

**Driven GitHub adapters**. The adapter is the subject, and the PyGithub `Repository` is the only collaborator
replaced. Everything the adapter does above that seam (choosing the call, filtering pull requests out of the issue
listing, mapping a `NamedUser` to a login, translating a `GithubException`) is real and is what the test covers. The
translation branch is covered in the same adapter test module, because the `RepositorySpy` raises a `GithubException`
on demand. No separate test category is needed for it.

**Environment adapter**. `ActionSettings.from_environment(environment=...)` reads the action inputs once from a
`Mapping[str, str]` and promotes the raw strings into typed values: the comma-separated assignees and assignment
options into tuples, `'true'` and `'false'` into booleans, and a missing or blank required input into
`MissingActionInput`, the typed exception owned by `src/driven/environment`. That promotion is behavior. Its only
consumer is the composition root, which is excluded from coverage, so no other test reaches it and the 100% gate
requires its own test.

**Logging**. A `logging.Logger` the driver writes to is the real standard-library logger, never a `Spy`. Assert a log
line through pytest `caplog` only when the line is part of the action's observable contract.

**Domain types covered through the model**:

- **Value objects used by a single model.** Their invariants are exercised when the model receives an input that the
  value object rejects. **Exception**: a dedicated test is admitted when the value object exposes standalone behavior
  unreachable through the model (rich parsing, arithmetic, ordering beyond `==`). A value object with only a
  constructor, its fields, and dataclass equality does NOT qualify.
- **Enums** (`StrEnum`, `IntEnum`, a `from_raw` parser). Covered through the model or driver that parses and uses
  each member. **Exception**: a dedicated enum test only when a per-member method has a truth table larger than the
  cases any single consumer exercises.
- **Domain exceptions.** Covered by the model test that drives the invariant violation and asserts the type with
  `pytest.raises`, reading the carried context off `raised.value` when it matters. A dedicated test module for an
  exception is NEVER justified.
- **Commands.** Frozen data carriers. Nothing to test directly.

## Worked shapes

### Domain model, a parameterized invariant

A matrix of inputs over one behavior is one test. The `ids` name each case in plain words, the argument names match
the test parameters, and the `# Given` states the shape the parameters fill.

```python
import pytest

from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.issue import Issue
from tests.support.builders.assignment_builder import AssignmentBuilder


@pytest.mark.parametrize(
    ids=['empty assignment denied', 'empty assignment allowed'],
    argnames=['allow_no_assignees'],
    argvalues=[(False,), (True,)]
)
def test_assign_when_actor_is_an_assignee_and_self_assignment_is_allowed_then_actor_is_assigned(
        allow_no_assignees: bool
) -> None:
    # Given an issue without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the actor assigns the issue to itself while self-assignment is allowed
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_actor(actor=Login(value='octocat'))
        .with_assignees(assignees=Logins.from_raw(values=('octocat',)))
        .with_allow_self_assign(allow_self_assign=True)
        .with_allow_no_assignees(allow_no_assignees=allow_no_assignees)
        .build()
    )

    # Then the actor is the assignee
    assert assigned_issue.assignees == Logins.from_raw(values=('octocat',))
```

Keyword arguments to `pytest.mark.parametrize` follow the ordering rule of `rules/python-code-style.md` (identifier
length ascending), which puts `ids` first.

### Handler with real models and outbound spies

```python
from src.application.commands.assign_issues import AssignIssues
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.issue import Issue
from src.application.handlers.issues_assigning_handler import IssuesAssigningHandler
from tests.support.spies.assignees_spy import AssigneesSpy
from tests.support.spies.issues_spy import IssuesSpy


def test_handle_when_issues_are_unassigned_then_each_is_assigned_to_the_accepted_assignees() -> None:
    # Given two unassigned issues
    issues = IssuesSpy(
        unassigned_issues=(
            Issue(number=1, author=Login(value='carol'), assignees=Logins.empty()),
            Issue(number=2, author=Login(value='dave'), assignees=Logins.empty())
        )
    )

    # And a repository that accepts only alice among the requested assignees
    handler = IssuesAssigningHandler(
        issues=issues,
        assignees=AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice',)))
    )

    # When the issues are assigned to alice and a stranger
    handler.handle(
        command=AssignIssues(
            actor='octocat',
            assignees=('alice', 'stranger'),
            skip_bots=False,
            skip_drafts=False,
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then both issues are assigned to alice only
    assert issues.assigned_issues == [
        Issue(number=1, author=Login(value='carol'), assignees=Logins.from_raw(values=('alice',))),
        Issue(number=2, author=Login(value='dave'), assignees=Logins.from_raw(values=('alice',)))
    ]
```

The refusal twin drives the same action with an input the model rejects, and checks that nothing reached the port. It
adds two imports to the module above:

```python
import pytest

from src.application.domain.exceptions.self_assignment_not_allowed import SelfAssignmentNotAllowed


def test_handle_when_actor_is_an_assignee_and_self_assign_is_denied_then_no_issue_is_assigned() -> None:
    # Given one unassigned issue
    issues = IssuesSpy(unassigned_issues=(Issue(number=1, author=Login(value='carol'), assignees=Logins.empty()),))

    # And a repository that accepts the actor and bob
    handler = IssuesAssigningHandler(
        issues=issues,
        assignees=AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice', 'bob')))
    )

    # Then the assignment fails because the actor would assign itself
    with pytest.raises(SelfAssignmentNotAllowed):
        # When the actor assigns the issue to a list that includes the actor
        handler.handle(
            command=AssignIssues(
                actor='alice',
                assignees=('alice', 'bob'),
                skip_bots=False,
                skip_drafts=False,
                assign_author=False,
                allow_self_assign=False,
                allow_no_assignees=False
            )
        )

    # And no issue was handed back to the port
    assert not issues.assigned_issues
```

### Console driver, one exit code per exception family

The driver catches each family once and maps it to one `Code`. A parameterized test makes the inbound `Spy` raise one
exception per family. Building the exception here is the stimulus the `Spy` raises, not the subject of the test.

```python
import logging

import pytest

from src.application.domain.exceptions.assignees_required import AssigneesRequired
from src.driver.console.assigners import Assigners
from src.driver.console.issues_assigner import IssuesAssigner
from src.driver.console.models.assignment_kind import AssignmentKind
from src.driver.console.models.code import Code
from src.driver.console.models.request import Request
from src.driver.console.pull_requests_and_issues_assigner import PullRequestsAndIssuesAssigner
from src.driver.console.pull_requests_assigner import PullRequestsAssigner
from tests.support.spies.issues_assigning_spy import IssuesAssigningSpy
from tests.support.spies.pull_requests_and_issues_assigning_spy import PullRequestsAndIssuesAssigningSpy
from tests.support.spies.pull_requests_assigning_spy import PullRequestsAssigningSpy


def request_for(assignment_options: tuple[str, ...]) -> Request:
    return Request(
        actor='octocat',
        assignees=('alice',),
        skip_bots=False,
        skip_drafts=False,
        assign_author=False,
        allow_self_assign=True,
        allow_no_assignees=False,
        assignment_options=assignment_options
    )


def assigners_over(
        issues: IssuesAssigningSpy,
        pull_requests: PullRequestsAssigningSpy,
        pull_requests_and_issues: PullRequestsAndIssuesAssigningSpy
) -> Assigners:
    return Assigners(
        logger=logging.getLogger('test'),
        assigners={
            AssignmentKind.ISSUES: IssuesAssigner(issues=issues),
            AssignmentKind.PULL_REQUESTS: PullRequestsAssigner(pull_requests=pull_requests),
            AssignmentKind.PULL_REQUESTS_AND_ISSUES: PullRequestsAndIssuesAssigner(
                pull_requests_and_issues=pull_requests_and_issues
            )
        }
    )


@pytest.mark.parametrize(
    ids=['domain rule violated', 'unexpected failure'],
    argnames=['failure', 'code'],
    argvalues=[(AssigneesRequired(), Code.ASSIGNMENT_FAILURE), (RuntimeError('boom'), Code.UNEXPECTED_FAILURE)]
)
def test_assign_when_the_use_case_fails_then_the_result_maps_the_failure_to_its_code(
        code: Code,
        failure: Exception
) -> None:
    # Given an issues use case that fails
    assigners = assigners_over(
        issues=IssuesAssigningSpy(failure=failure),
        pull_requests=PullRequestsAssigningSpy(),
        pull_requests_and_issues=PullRequestsAndIssuesAssigningSpy()
    )

    # When issues are requested
    result = assigners.assign(request=request_for(assignment_options=('ISSUE',)))

    # Then the result carries the code of that failure
    assert result.code == code
```

The configuration family (`InvalidAssignmentOptions` under `src/driver/exceptions`) is raised inside the driver by
`AssignmentKind.from_options` while it reads the request, so its test needs no failing `Spy`: an unknown option in
`assignment_options` drives `Code.CONFIGURATION_MISSING`. A family raised below the driver by a driven adapter
(`GitHubRequestFailed`, owned by `src/driven/github`) reaches the driver through `except Exception`, so the
`unexpected failure` row above covers it. The `Request` and the `Assigners` repeat across every test of the module, so
they come from the module-level helpers `request_for` and `assigners_over` (`references/test-data-builder.md`). The
helper builds the mapping with the real assigners over the `Spy` inbound ports, because an assigner lives inside the
hexagon. Each assigner also has its own test module, which asserts the command its inbound port receives.

## When a dedicated non-root test IS justified

A dedicated test for a domain type other than a model requires one of these reasons:

- "Behavior X cannot be reached through model Y because it requires state Z that the model refuses to enter."
  (Design smell. Prefer refactoring to expose the path through the model.)
- "This value object is consumed by N models and has standalone parsing or arithmetic worth isolating."
- "This enum has a per-member method whose truth table is larger than the cases any single consumer exercises."

`rules/python-code-style.md` prohibits justification comments in code, so the reason goes in the change summary, the
same place `rules/python-design-principles.md` records a SHOULD deviation. A dedicated test without a recorded reason
is surplus and must be removed. The escape hatch is for domain types only, never for a driver support type or a
`src/driven/` helper.

## Testing a domain exception through the raising behavior

A domain exception is a pure invariant-violation signal owned by the domain. A test builds the conditions, invokes the
public method that is supposed to fail inside `pytest.raises(X)`, and asserts the type. Constructing the exception
directly and asserting on its attributes is prohibited: no production code runs. The shapes live in
`references/exception-assertion.md`.

If no public method has a call path that raises the exception, the exception is dead code. Remove it instead of writing
a test against its constructor.
