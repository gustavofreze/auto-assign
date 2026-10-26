# Ports and adapters, in depth

Deep detail behind the `python-applying-hexagonal-architecture` skill. Generic and language-agnostic, with short Python
examples on the action's own vocabulary (Issue, PullRequest, Assignee, Actor) and the adapters the layout names.
The examples are trimmed to the fields each point needs. The enforced specifics for this repository (folder layout,
naming, error placement) live in `rules/python-architecture.md` and `rules/python-domain.md`. This file teaches the
universal concept only.

## Contents

- The dependency rule
- The runnable-core test
- Ports: inbound versus outbound
- Adapters: driver versus driven
- The composition root
- The anti-corruption boundary
- Putting it together

## The dependency rule

Source-code dependencies point inward only. Draw the system as concentric rings: the domain
(`src/application/domain/`) at the center, the surrounding application (`src/application/commands/`,
`src/application/ports/`, `src/application/handlers/`, `src/application/requested_assignment.py`), the adapters on
the outside (`src/driver/`, `src/driven/`), the composition root (`src/dependencies.py`, `src/main.py`) furthest out.
A name resolved in an inner ring may never import a name from an outer ring. The domain imports nothing from the
application. The application imports nothing from the adapters. Adapters may import inward. The reverse never
happens.

Control flow and source dependency point in opposite directions across an outbound boundary, and that opposition is
the whole trick. A run flows inward (the console driver calls an inbound port, the handler behind it runs), then the
handler needs to reach back out to GitHub, yet the source dependency of that reach still points inward: the handler
depends on an outbound port the core owns, and the GitHub adapter depends on that same port from the outside.

In Python the inversion is carried by an explicit `ABC` subclass. The port lives in the core
(`src/application/ports/outbound/`), and the adapter names it in its class statement, so the dependency is visible in
the source and checked by `mypy --strict`.

```python
# src/application/ports/outbound/issues.py
# Inner ring (core) owns the contract. Docstrings live here, on the port, and nowhere else.
from abc import ABC, abstractmethod

from src.application.domain.models.issue import Issue


class Issues(ABC):
    """Open issues of the repository."""

    @abstractmethod
    def unassigned(self) -> tuple[Issue, ...]:
        """Lists the open issues that have no assignee.

        :returns: The open issues without an assignee.
        """

    @abstractmethod
    def assign(self, issue: Issue) -> None:
        """Records the assignees of the issue in the repository.

        :param issue: The issue carrying its granted assignees.
        """
```

```python
# src/driven/github/github_issues.py
# Outer ring (adapter) depends on the inner contract, not the reverse.
# No docstring on the concrete adapter. The port already states the contract.
from typing import final

from github.Repository import Repository

from src.application.domain.models.issue import Issue
from src.application.ports.outbound.issues import Issues
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_issue_records import GitHubIssueRecords


@final
class GitHubIssues(Issues):

    def __init__(self, records: GitHubIssueRecords, journal: AssignmentJournal, repository: Repository) -> None:
        self._records = records
        self._journal = journal
        self._repository = repository

    def unassigned(self) -> tuple[Issue, ...]:
        ...

    def assign(self, issue: Issue) -> None:
        ...
```

The port returns a `tuple`, never a `list` or a `PaginatedList`. An empty tuple means "nothing awaits an assignee",
and only that. A failed call is never an empty tuple, it is a typed exception (see § The anti-corruption boundary).

## The runnable-core test

Cockburn's framing: you should be able to run the application with no real transport and no external process. Make the
test operational by exercising a handler with every outbound port replaced by a hand-written `Spy` that implements the
same `ABC`. No GitHub, no token, no network.

```python
# tests/support/spies/issues_spy.py
# A boundary double: implements the outbound port and records what the handler told it.
from typing import final

from src.application.domain.models.issue import Issue
from src.application.ports.outbound.issues import Issues


@final
class IssuesSpy(Issues):

    def __init__(self, unassigned_issues: tuple[Issue, ...]) -> None:
        self.assigned_issues: list[Issue] = []
        self._unassigned_issues = unassigned_issues

    def unassigned(self) -> tuple[Issue, ...]:
        return self._unassigned_issues

    def assign(self, issue: Issue) -> None:
        self.assigned_issues.append(issue)
```

```python
# tests/support/spies/assignees_spy.py
from typing import final

from src.application.domain.models.commons.logins import Logins
from src.application.ports.outbound.assignees import Assignees


@final
class AssigneesSpy(Assignees):

    def __init__(self, assignable_logins: Logins) -> None:
        self.requested_logins: list[Logins] = []
        self._assignable_logins = assignable_logins

    def assignable(self, logins: Logins) -> Logins:
        self.requested_logins.append(logins)
        return self._assignable_logins
```

```python
# tests/application/handlers/test_issues_assigning_handler.py
# The same handler runs unchanged against the spies. The Issue model inside it is the real one.
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

If the handler runs here, the core is free of infrastructure. If it cannot run without a token, a PyGithub client, or
an environment variable set at import time, an outward dependency leaked inward. Find it and invert it behind a port.
The double conventions themselves (the `Spy` suffix, Given/When/Then with one `# When`, no `unittest.mock`) are owned
by `rules/python-testing.md` and the `python-writing-tests` skill. This test is only about the architecture, not the
test style.

## Ports: inbound versus outbound

A port is an `ABC` the core owns. The core depends on the `ABC`, never on whatever implements it. Ports come in two
kinds, distinguished by who drives whom.

| Kind     | Also called       | Direction of control        | Implemented by       | Example in this action                     |
|----------|-------------------|-----------------------------|----------------------|--------------------------------------------|
| Inbound  | Driving, primary  | The outside drives the core | The core (a handler) | `IssuesAssigning`, `PullRequestsAssigning` |
| Outbound | Driven, secondary | The core drives the outside | A driven adapter     | `Issues`, `PullRequests`, `Assignees`      |

An inbound port states one use case as one contract, typed on its own command. The console driver builds the command
and calls the port. Exactly one handler implements the port.

```python
# src/application/ports/inbound/issues_assigning.py
from abc import ABC, abstractmethod

from src.application.commands.assign_issues import AssignIssues


class IssuesAssigning(ABC):
    """Assigning of the open issues that have no assignee yet."""

    @abstractmethod
    def handle(self, command: AssignIssues) -> None:
        """Assigns every open issue without an assignee to the assignees the repository accepts.

        :param command: The assignment requested by the actor.
        :raises AssigneesRequired: When no assignee remains and an empty assignment is not allowed.
        :raises SelfAssignmentNotAllowed: When the actor is among the assignees and self-assignment is denied.
        """
```

The command is the typed input to that one use case: a `@final` frozen dataclass named as an imperative intent,
holding primitives only (builtins and tuples of builtins), never a domain type and never a raw transport shape. It
carries no behavior. The three use cases share their fields, so they extend one non-final base and each stays an
empty `@final` subclass. The handler promotes the primitives into value objects through `RequestedAssignment`.

```python
# src/application/commands/assignment_command.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AssignmentCommand:
    actor: str
    assignees: tuple[str, ...]
    skip_bots: bool
    skip_drafts: bool
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool
```

```python
# src/application/commands/assign_issues.py
from dataclasses import dataclass
from typing import final

from src.application.commands.assignment_command import AssignmentCommand


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AssignIssues(AssignmentCommand):
    pass
```

A single generic port shared by every use case is the shape to avoid. Each handler would narrow the parameter type of
`handle`, which is a Liskov violation, and the port would name no use case at all.

```python
# WRONG. One port for every use case. IssuesAssigningHandler.handle(command: AssignIssues) narrows the parameter.
class CommandHandler(ABC):

    @abstractmethod
    def handle(self, command: Command) -> None:
        ...
```

The handler implements the inbound port and depends only on outbound ports, the domain, and the application
collaborators at the `src/application/` root. It asks a port for the work, returns early when there is none, turns
the command into an `Assignment` through `RequestedAssignment`, tells each model to act, and hands the outcome back to
a port. The rule (who may be assigned, whether the actor may assign to themselves, which items are skipped) lives in
the domain, on the `Assignment` value object the models share, not in the handler.

```python
# src/application/handlers/issues_assigning_handler.py
from typing import final

from src.application.commands.assign_issues import AssignIssues
from src.application.requested_assignment import RequestedAssignment
from src.application.ports.inbound.issues_assigning import IssuesAssigning
from src.application.ports.outbound.assignees import Assignees
from src.application.ports.outbound.issues import Issues


@final
class IssuesAssigningHandler(IssuesAssigning):

    def __init__(self, issues: Issues, assignees: Assignees) -> None:
        self._issues = issues
        self._requested_assignment = RequestedAssignment(assignees=assignees)

    def handle(self, command: AssignIssues) -> None:
        unassigned = self._issues.unassigned()

        if not unassigned:
            return

        assignment = self._requested_assignment.from_command(command=command)

        for issue in unassigned:
            self._issues.assign(issue=issue.assign(assignment=assignment))
```

The promotion every handler repeats lives in one `@final` collaborator at the `src/application/` root, beside
`commands/` and `handlers/`, never inside `handlers/`, because a handler never imports from `src.application.handlers`.
It is not a port and the composition root never wires it: each handler builds one in its constructor from the
`Assignees` port it received.

```python
# src/application/requested_assignment.py
from typing import final

from src.application.commands.assignment_command import AssignmentCommand
from src.application.domain.models.commons.assignment import Assignment
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.ports.outbound.assignees import Assignees


@final
class RequestedAssignment:

    def __init__(self, assignees: Assignees) -> None:
        self._assignees = assignees

    def from_command(self, command: AssignmentCommand) -> Assignment:
        return Assignment(
            actor=Login(value=command.actor),
            assignees=self._assignees.assignable(logins=Logins.from_raw(values=command.assignees)),
            eligibility=Eligibility(skip_bots=command.skip_bots, skip_drafts=command.skip_drafts),
            assign_author=command.assign_author,
            allow_self_assign=command.allow_self_assign,
            allow_no_assignees=command.allow_no_assignees
        )
```

The model the handler tells to act is a frozen dataclass whose transition returns a new instance, or itself when the
assignment excludes it. The invariant is raised as a domain exception from inside the `Assignment` value object, which
`Issue` and `PullRequest` both take, so every handler that assigns an issue or a pull request gets the same rule.

```python
# src/application/domain/models/commons/assignment.py
from dataclasses import dataclass
from typing import final

from src.application.domain.exceptions.assignees_required import AssigneesRequired
from src.application.domain.exceptions.self_assignment_not_allowed import SelfAssignmentNotAllowed
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Assignment:
    actor: Login
    assignees: Logins
    eligibility: Eligibility
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool

    def excludes(self, author: Login, draft: bool) -> bool:
        return self.eligibility.excludes(author=author, draft=draft)

    def granted_assignees(self, author: Login) -> Logins:
        authors = Logins(elements=(author,)) if self.assign_author else Logins.empty()

        if not self.assignees and not authors and not self.allow_no_assignees:
            raise AssigneesRequired()

        if self.actor not in self.assignees or self.allow_self_assign:
            return self.assignees.including(other=authors)

        if not self.allow_no_assignees:
            raise SelfAssignmentNotAllowed(actor=self.actor)

        return self.assignees.without(login=self.actor).including(other=authors)
```

```python
# src/application/domain/models/issue.py
from dataclasses import dataclass
from typing import final

from src.application.domain.models.commons.assignment import Assignment
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Issue:
    number: int
    author: Login
    assignees: Logins

    def assign(self, assignment: Assignment) -> Issue:
        if assignment.excludes(author=self.author, draft=False):
            return self

        return Issue(number=self.number, author=self.author, assignees=assignment.granted_assignees(author=self.author))
```

A use case that spans two kinds of item never invokes another handler or inbound port. It talks to the outbound ports
of both kinds directly, builds one `Assignment`, and lets each model apply it. The rule both kinds share already lives
on that value object, so nothing is duplicated.

```python
# src/application/handlers/pull_requests_and_issues_assigning_handler.py
@final
class PullRequestsAndIssuesAssigningHandler(PullRequestsAndIssuesAssigning):

    def __init__(self, issues: Issues, assignees: Assignees, pull_requests: PullRequests) -> None:
        self._issues = issues
        self._requested_assignment = RequestedAssignment(assignees=assignees)
        self._pull_requests = pull_requests

    def handle(self, command: AssignPullRequestsAndIssues) -> None:
        unassigned_pull_requests = self._pull_requests.unassigned()
        unassigned_issues = self._issues.unassigned()

        if not unassigned_pull_requests and not unassigned_issues:
            return

        assignment = self._requested_assignment.from_command(command=command)

        for pull_request in unassigned_pull_requests:
            self._pull_requests.assign(pull_request=pull_request.assign(assignment=assignment))

        for issue in unassigned_issues:
            self._issues.assign(issue=issue.assign(assignment=assignment))
```

An outbound port states a capability the core needs, expressed entirely in domain terms. No PyGithub `Repository`, no
`PaginatedList`, no `NamedUser`, no `GithubException` appears in the signature. The adapter performs the translation
to and from the transport form.

```python
# src/application/ports/outbound/assignees.py
# Stated in domain types only. The adapter turns logins into a PyGithub lookup.
from abc import ABC, abstractmethod

from src.application.domain.models.commons.logins import Logins


class Assignees(ABC):
    """Members the repository accepts as assignees."""

    @abstractmethod
    def assignable(self, logins: Logins) -> Logins:
        """Selects the logins the repository accepts as assignees, keeping their order.

        :param logins: The logins requested as assignees.
        :returns: The requested logins the repository accepts.
        """
```

A port that leaks a vendor type is a fake inversion. The contract below couples every handler to PyGithub, so swapping
the technology, or running the handler under a `Spy`, forces a change in the core.

```python
# WRONG. A PyGithub Repository goes in and a PaginatedList of PyGithub issues comes out.
class Issues(ABC):

    @abstractmethod
    def unassigned(self, repository: Repository) -> PaginatedList[Issue]:
        ...
```

## Adapters: driver versus driven

An adapter is a concrete `@final` class that speaks one specific technology. It sits outside the core, on one side of
a port.

A **driving adapter (primary)** is on the inbound side. It receives input from a real transport, builds the command,
and calls the inbound port. In a web service that transport is HTTP. In this action it is the GitHub Actions runner,
read into a `Request` before the driver sees it. The console driver owns nothing about the use case itself. One
`Assigner` per assignment kind builds the command from the `Request` and calls its inbound port. `Assigners` resolves
the kind, picks the matching `Assigner` from a mapping, and maps each exception family to one exit `Code`, once.
Nothing below it knows about exit codes.

```python
# src/driver/console/assigner.py
from abc import ABC, abstractmethod

from src.driver.console.models.request import Request


class Assigner(ABC):
    """Assignment of one kind of repository item requested by the action."""

    @abstractmethod
    def assign(self, request: Request) -> None:
        """Assigns the items of its kind according to the action request.

        :param request: The action request carrying the actor, the assignees, and the self-assignment flags.
        """
```

```python
# src/driver/console/issues_assigner.py
from typing import final

from src.application.commands.assign_issues import AssignIssues
from src.application.ports.inbound.issues_assigning import IssuesAssigning
from src.driver.console.assigner import Assigner
from src.driver.console.models.request import Request


@final
class IssuesAssigner(Assigner):

    def __init__(self, issues: IssuesAssigning) -> None:
        self._issues = issues

    def assign(self, request: Request) -> None:
        command = AssignIssues(
            actor=request.actor,
            assignees=request.assignees,
            skip_bots=request.skip_bots,
            skip_drafts=request.skip_drafts,
            assign_author=request.assign_author,
            allow_self_assign=request.allow_self_assign,
            allow_no_assignees=request.allow_no_assignees
        )
        self._issues.handle(command=command)
```

```python
# src/driver/console/assigners.py
import logging
from collections.abc import Mapping
from typing import final

from src.application.domain.exceptions.domain_exception import DomainException
from src.driver.console.assigner import Assigner
from src.driver.console.models.assignment_kind import AssignmentKind
from src.driver.console.models.request import Request
from src.driver.console.models.result import Result
from src.driver.exceptions.invalid_assignment_options import InvalidAssignmentOptions


@final
class Assigners:

    def __init__(self, logger: logging.Logger, assigners: Mapping[AssignmentKind, Assigner]) -> None:
        self._logger = logger
        self._assigners = assigners

    def assign(self, request: Request) -> Result:
        try:
            kind = AssignmentKind.from_options(options=request.assignment_options)
            self._assigners[kind].assign(request=request)
        except InvalidAssignmentOptions as invalid_options:
            self._logger.exception(str(invalid_options), exc_info=False)
            return Result.configuration_missing(message=str(invalid_options))
        except DomainException as assignment_failure:
            self._logger.exception(str(assignment_failure), exc_info=False)
            return Result.assignment_failure(message=str(assignment_failure))
        except Exception as unexpected_failure:
            self._logger.exception(str(unexpected_failure))
            return Result.unexpected_failure(message=str(unexpected_failure))

        return Result.success()
```

An expected failure (a configuration or domain family) is logged without its traceback (`exc_info=False`), only an
unexpected one carries it. `src/main.py` installs `AnnotationFormatter` on the logger, which prefixes each error and
warning line with the `::error::` or `::warning::` workflow command, so the runner surfaces it as an annotation.

A **driven adapter (secondary)** is on the outbound side. It implements one outbound port and owns the transport (a
PyGithub call, an environment read). It translates between the domain and the technology in both directions, and it
translates the technology's failures into the typed exception its own package owns (`GitHubRequestFailed`). Choosing
which records a run covers is a separate collaborator (`GitHubIssueRecords`), and so is keeping the account of what
the run assigned (`AssignmentJournal`), so the adapter keeps no private helper.

```python
# src/driven/github/github_issues.py
from typing import final

from github import GithubException
from github.Repository import Repository

from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.issue import Issue
from src.application.ports.outbound.issues import Issues
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_issue_records import GitHubIssueRecords
from src.driven.github.github_request_failed import GitHubRequestFailed
from src.driven.github.item_kind import ItemKind
from src.driven.github.journal_entry import JournalEntry

OPEN_STATE = 'open'


@final
class GitHubIssues(Issues):

    def __init__(self, records: GitHubIssueRecords, journal: AssignmentJournal, repository: Repository) -> None:
        self._records = records
        self._journal = journal
        self._repository = repository

    def unassigned(self) -> tuple[Issue, ...]:
        try:
            return tuple(
                Issue(number=record.number, author=Login(value=record.user.login), assignees=Logins.empty())
                for record in self._records.in_scope()
                if record.state == OPEN_STATE and not record.assignees and record.pull_request is None
            )
        except GithubException as listing_failure:
            raise GitHubRequestFailed(status=listing_failure.status, operation='list issues') from listing_failure

    def assign(self, issue: Issue) -> None:
        if not issue.assignees:
            return

        try:
            record = self._repository.get_issue(number=issue.number)
            record.add_to_assignees(*(assignee.value for assignee in issue.assignees))
        except GithubException as assignment_failure:
            raise GitHubRequestFailed(
                status=assignment_failure.status,
                operation='assign an issue'
            ) from assignment_failure

        self._journal.record(
            entry=JournalEntry(
                kind=ItemKind.ISSUE,
                number=issue.number,
                assignees=tuple(assignee.login for assignee in record.assignees)
            )
        )
```

`GitHubPullRequests` has the same shape. It also copies `record.draft` onto the `PullRequest`, and it assigns through
`repository.get_issue(...)` as well, because GitHub adds assignees to a pull request through its issue.
`AssignmentJournal` is one instance shared by both adapters for the run. Each records a `JournalEntry` holding the
assignees the record carries after the write, and the composition root reads the journal back as the action outputs
and the step summary.

```python
# src/driven/github/github_issue_records.py
from typing import final

from github.Issue import Issue
from github.Repository import Repository

UNASSIGNED = 'none'


@final
class GitHubIssueRecords:

    def __init__(self, repository: Repository, triggering_numbers: tuple[int, ...] | None) -> None:
        self._repository = repository
        self._triggering_numbers = triggering_numbers

    def in_scope(self) -> tuple[Issue, ...]:
        if self._triggering_numbers is None:
            return tuple(self._repository.get_issues(assignee=UNASSIGNED))

        return tuple(self._repository.get_issue(number=number) for number in self._triggering_numbers)
```

```python
# src/driven/github/github_request_failed.py
# One typed exception for every GitHub call the package makes. The operation names which call failed.
from typing import final


@final
class GitHubRequestFailed(Exception):

    def __init__(self, status: int, operation: str) -> None:
        super().__init__(f'GitHub request to {operation} failed with status <{status}>.')
```

`ActionSettings` under `src/driven/environment/` is a driven adapter too, but no handler needs it, so it implements no
outbound port. `ActionSettings.from_environment(environment=...)` reads the action inputs once from a
`Mapping[str, str]`, promotes them into typed values (tuples of logins and assignment options, the `bool` flags
grouped in `AssignmentPreferences`, the `TriggeringEvent`, the repository name, the token), and hands them to the
composition root. A missing input is raised there as `MissingActionInput`, the typed exception the environment
package owns, never as a `KeyError` from deep inside the run. `ActionOutput` is its counterpart on the way out: it
appends the outputs to `GITHUB_OUTPUT` and the summary to `GITHUB_STEP_SUMMARY`, and only `src/main.py` calls it.

The two sides follow opposite naming conventions on purpose. A driver is named for what it exposes (`Assigners`,
`IssuesAssigner`). A driven adapter is named for the technology plus the capability it implements (`GitHubIssues`,
`GitHubAssignees`, `ActionSettings`), in a module named after it (`github_issues.py`). The bare
name `Adapter` says nothing, because every repository, gateway, and client is an adapter. The enforced naming for this
repository is owned by `rules/python-architecture.md` § Driven adapter conventions.

## The composition root

The composition root is the single place in the system that knows the concrete adapters and handlers. It builds the
object graph and injects each concrete through its port. Nothing else constructs an adapter or a handler, and no
module under `src/application/` or `src/driver/` ever calls a driven adapter's constructor.

In this action the root is `src/dependencies.py`, a declarative `dependency_injector` container, together with
`src/main.py`, the process entry point. The container declares providers and nothing else: no business logic, no
validation, no guard that raises.

```python
# src/dependencies.py
# One place wires the graph. Swap an adapter here without touching the core.
import logging

from dependency_injector import containers, providers
from github import Auth, Github

from src.application.handlers.issues_assigning_handler import IssuesAssigningHandler
from src.application.handlers.pull_requests_and_issues_assigning_handler import PullRequestsAndIssuesAssigningHandler
from src.application.handlers.pull_requests_assigning_handler import PullRequestsAssigningHandler
from src.driven.environment.action_settings import ActionSettings
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_assignees import GitHubAssignees
from src.driven.github.github_issue_records import GitHubIssueRecords
from src.driven.github.github_issues import GitHubIssues
from src.driven.github.github_pull_request_records import GitHubPullRequestRecords
from src.driven.github.github_pull_requests import GitHubPullRequests
from src.driver.console.assigners import Assigners
from src.driver.console.issues_assigner import IssuesAssigner
from src.driver.console.models.assignment_kind import AssignmentKind
from src.driver.console.pull_requests_and_issues_assigner import PullRequestsAndIssuesAssigner
from src.driver.console.pull_requests_assigner import PullRequestsAssigner

PAGE_SIZE = 100
GITHUB_API_VERSION = '2026-03-10'


class Dependencies(containers.DeclarativeContainer):
    journal = providers.Dependency(instance_of=AssignmentJournal)
    settings = providers.Dependency(instance_of=ActionSettings)

    client = providers.Singleton(
        Github,
        auth=providers.Factory(Auth.Token, settings.provided.github_token),
        # Lazy objects skip the GET that would fetch a repository or an item before writing to it.
        lazy=True,
        per_page=PAGE_SIZE,
        api_version=GITHUB_API_VERSION
    )

    repository = providers.Singleton(
        lambda client, name: client.get_repo(name),
        client=client,
        name=settings.provided.repository
    )

    issue_records = providers.Singleton(
        GitHubIssueRecords,
        repository=repository,
        triggering_numbers=settings.provided.event.issue_numbers
    )

    issues = providers.Singleton(GitHubIssues, records=issue_records, journal=journal, repository=repository)

    assignees = providers.Singleton(GitHubAssignees, repository=repository)

    pull_request_records = providers.Singleton(
        GitHubPullRequestRecords,
        repository=repository,
        triggering_numbers=settings.provided.event.pull_request_numbers
    )

    pull_requests = providers.Singleton(
        GitHubPullRequests,
        records=pull_request_records,
        journal=journal,
        repository=repository
    )

    assign_issues = providers.Factory(IssuesAssigningHandler, issues=issues, assignees=assignees)

    assign_pull_requests = providers.Factory(
        PullRequestsAssigningHandler,
        assignees=assignees,
        pull_requests=pull_requests
    )

    assign_pull_requests_and_issues = providers.Factory(
        PullRequestsAndIssuesAssigningHandler,
        issues=issues,
        assignees=assignees,
        pull_requests=pull_requests
    )

    assigners = providers.Singleton(
        Assigners,
        logger=logging.getLogger('auto-assign'),
        assigners=providers.Dict({
            AssignmentKind.ISSUES: providers.Factory(IssuesAssigner, issues=assign_issues),
            AssignmentKind.PULL_REQUESTS: providers.Factory(PullRequestsAssigner, pull_requests=assign_pull_requests),
            AssignmentKind.PULL_REQUESTS_AND_ISSUES: providers.Factory(
                PullRequestsAndIssuesAssigner,
                pull_requests_and_issues=assign_pull_requests_and_issues
            )
        })
    )
```

```python
# src/main.py
# The entry point reads the settings once, runs the driver, and writes the action outputs and step summary.
import logging
import os
from collections.abc import Mapping

from src.dependencies import Dependencies
from src.driven.environment.action_output import ActionOutput
from src.driven.environment.action_settings import ActionSettings
from src.driven.environment.missing_action_input import MissingActionInput
from src.driven.environment.triggering_event_unreadable import TriggeringEventUnreadable
from src.driven.github.assignment_journal import AssignmentJournal
from src.driver.console.annotation_formatter import AnnotationFormatter
from src.driver.console.models.request import Request
from src.driver.console.models.result import Result

LOGGER = logging.getLogger('auto-assign')


def run(environment: Mapping[str, str], journal: AssignmentJournal) -> Result:
    try:
        settings = ActionSettings.from_environment(environment=environment)
    except (MissingActionInput, TriggeringEventUnreadable) as invalid_configuration:
        LOGGER.exception(str(invalid_configuration), exc_info=False)
        return Result.configuration_missing(message=str(invalid_configuration))
    except Exception as settings_failure:
        LOGGER.exception(str(settings_failure))
        return Result.unexpected_failure(message=str(settings_failure))

    try:
        assigners = Dependencies(settings=settings, journal=journal).assigners()
    except Exception as wiring_failure:
        LOGGER.exception(str(wiring_failure))
        return Result.unexpected_failure(message=str(wiring_failure))

    request = Request(
        actor=settings.actor,
        assignees=settings.assignees,
        skip_bots=settings.preferences.skip_bots,
        skip_drafts=settings.preferences.skip_drafts,
        assign_author=settings.preferences.assign_author,
        allow_self_assign=settings.preferences.allow_self_assign,
        allow_no_assignees=settings.preferences.allow_no_assignees,
        assignment_options=settings.assignment_options
    )

    return assigners.assign(request=request)


if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(AnnotationFormatter())
    LOGGER.addHandler(handler)

    output_path = os.environ.get('GITHUB_OUTPUT', '')

    if output_path == '':
        LOGGER.warning('GITHUB_OUTPUT is not set, so the action outputs are not written.')

    assignment_journal = AssignmentJournal()
    result = run(environment=os.environ, journal=assignment_journal)

    ActionOutput(
        output_path=output_path,
        summary_path=os.environ.get('GITHUB_STEP_SUMMARY', '')
    ).write(
        outputs={
            'result': result.to_json(
                issues=assignment_journal.issues(),
                pull_requests=assignment_journal.pull_requests()
            )
        },
        summary=assignment_journal.summary()
    )
```

The journal is built in `src/main.py`, outside the container, and handed in as a `providers.Dependency`, because the
entry point reads it back after the run to write the outputs and the summary, even when the run failed.

When configuration decides how a concrete behaves, the *decision* lives in the root, as a provider fed by the
settings, never as a branch inside the core. The triggering event is wired this way: the root hands
`settings.provided.event.issue_numbers` to `GitHubIssueRecords`, where `None` scans the repository for unassigned
issues and a tuple lists only the item that triggered the run. Choosing which use case a run serves is not a wiring
decision: the assignment options are action input, so the console driver parses them (`AssignmentKind.from_options`)
and calls the matching `Assigner`, which calls one inbound port.

Constructor injection keeps every dependency explicit and every collaborator a port. Because the wiring lives in one
place, a test builds the same handler over `Spy` doubles, and production wires it to the GitHub adapters, with no
change to the core. The principle side of this (inversion, single responsibility) is owned by
`rules/python-design-principles.md` and the `python-applying-design-principles` skill.

## The anti-corruption boundary

Foreign concepts (a PyGithub `Issue`, a `NamedUser`, a `PaginatedList`, a `GithubException`) are translated into this
system's vocabulary at the adapter boundary. The translation lives in the driven adapter, never in the handler and
never in the domain. The core stays expressed in its own ubiquitous language, protected from the shape of whatever it
integrates with.

`GitHubIssues` above shows the three translations an adapter owns:

1. **Shape.** A PyGithub issue becomes a domain `Issue` with a number, its author `Login`, and its `Logins`, and a
   granted `Login` goes back out as its plain `value`. The handler never sees an attribute PyGithub defines.
2. **Meaning.** The GitHub issues endpoint also returns pull requests. Filtering them out (`pull_request is None`) is
   knowledge about the foreign API, so it lives in the adapter, not in the domain and not in the handler.
3. **Failure.** A `GithubException` is caught inside the adapter and re-raised as `GitHubRequestFailed`, the typed
   exception the `src/driven/github` package owns, chained with `from`. It is never swallowed into an empty tuple,
   because an empty result means "nothing found", never "the call failed".

When the translation grows beyond a single mapping (paging rules, a catalog of GitHub states, selection over it), that
logic belongs *inside the adapter behind the port*, not in the domain. A rule that selects over an external catalog is
an adapter concern, because the domain must not learn the catalog's shape.

**Anti-patterns to reject at review time.**

- A `github` import, a `PaginatedList`, or a `GithubException` appearing anywhere under `src/application/`.
- A PyGithub object passed to a domain method instead of being mapped first.
- A `match` over GitHub states or error codes living in a domain model rather than in the adapter that owns them.
- A handler or the driver constructing a driven adapter (`GitHubIssues(...)`) instead of receiving the port by
  injection.
- An outbound port method whose signature names a vendor type (`Repository`, `NamedUser`, `PaginatedList`).
- An `except GithubException` that returns an empty tuple, `None`, or `False`.

## Putting it together

The flow of one assignment, end to end, as it runs in this action:

1. `src/main.py` reads `ActionSettings` once and builds the container and the `Request`.
2. The console driver builds the command from the request and calls the inbound port.
3. The handler behind the port asks the outbound ports for the work (the unassigned issues, then the assignable
   logins), returning early when nothing is unassigned.
4. The handler tells each model to act. The model enforces the invariants and raises a domain exception on a violation.
5. The handler hands each outcome to an outbound port. Driven adapters fulfill those ports, owning the transport and
   translating at the boundary in both directions.
6. The driver maps the outcome, or the exception family, to one exit `Code`, and `src/main.py` writes it, with the
   numbers and the summary the `AssignmentJournal` kept, through `ActionOutput`.
7. The composition root in `src/dependencies.py` decided, once, which concrete adapters and handlers back those
   ports.

At no step does an inner ring import an outer one. That is the property the architecture buys, and the runnable-core
test is how you confirm you still have it.
