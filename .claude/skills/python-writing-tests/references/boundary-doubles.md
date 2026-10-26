# Doubling the boundary

Read this while writing a `Spy` or a test that runs against one: a handler over its outbound ports, the console driver
over its inbound ports, a GitHub adapter over the PyGithub `Repository`, or the environment adapter over the process
environment. The policy (real objects inside the hexagon, hand-written doubles ending in `Spy` only at a boundary, no
`unittest.mock`, `MagicMock`, or `patch`) is owned by `rules/python-testing.md` § Doubles. This file holds the shapes
and the recording how-to.

## At a glance

| Question                 | Answer                                                                                                                                                                           |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| What gets a `Spy`?       | An outbound port in a handler test, an inbound port in a driver test, the PyGithub `Repository` and its objects in a GitHub adapter test.                                        |
| What never gets a `Spy`? | A model, a value object, a command, the adapter under test, the standard-library logger.                                                                                         |
| Where does a `Spy` live? | `tests/support/spies/<name>_spy.py`, one public class per module, the PyGithub object spies (`RecordSpy`, `UserSpy`) included.                                                   |
| How does it record?      | Plain public attributes (`assigned_issues`, `commands`, `added_assignees`, `requested`) the test reads in the `# Then`.                                                          |
| How is it configured?    | Constructor arguments only (`IssuesSpy(unassigned_issues=...)`, `IssuesAssigningSpy(failure=None)`, `RepositorySpy(records=..., members=..., failure=...)`).                     |
| What do I assert?        | (1) the returned value or exit `Code`, (2) the calls the `Spy` recorded, (3) the typed exception a failure becomes.                                                              |
| An unexpected call?      | It fails loudly: an unseeded record lookup raises `StopIteration`, an unmodeled member raises `AttributeError`. Never a silent `None`.                                           |
| The environment?         | A plain `dict` handed to `ActionSettings.from_environment(environment=...)`. No `monkeypatch`, and never `monkeypatch.setattr`.                                                  |

## Shape of a `Spy`

Every `Spy` is a `@final` class that follows `rules/python-code-style.md` like production code: full annotations, no
`else`, keyword arguments, no docstrings (it is a concrete class). It **implements** the port `ABC` it replaces
(`class IssuesSpy(Issues)`), or **duck-types** the third-party seam it replaces, with no base class (`class
RepositorySpy`). It records calls in public attributes, because the test reads them, and it holds no logic beyond
returning what it was seeded with, raising what it was told to raise, and recording.

A variable holding a `Spy` is named for the business concept it stands in for (`issues`, `repository`), never `spy`,
`mock`, or `fake`.

## Outbound port spies (handler tests)

```python
# tests/support/spies/issues_spy.py
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

`AssigneesSpy(Assignees)` and `PullRequestsSpy(PullRequests)` follow the same shape: seeded with what the port answers
(`AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice', 'bob')))`,
`PullRequestsSpy(unassigned_pull_requests=...)`), recording what the handler hands over (`requested_logins`,
`assigned_pull_requests`). The handler test asserts the recorded list by value equality against real domain models
(`[Issue(number=1, author=Login(value='carol'), assignees=Logins.from_raw(values=('alice',)))]`).

## Inbound port spies (console driver tests)

The console driver depends on one inbound port per use case. Its test replaces each with a `Spy` that records the
command and, when told to, raises one exception so the driver's exit-code mapping runs.

```python
# tests/support/spies/issues_assigning_spy.py
from typing import final

from src.application.commands.assign_issues import AssignIssues
from src.application.ports.inbound.issues_assigning import IssuesAssigning


@final
class IssuesAssigningSpy(IssuesAssigning):

    def __init__(self, failure: Exception | None) -> None:
        self.commands: list[AssignIssues] = []
        self._failure = failure

    def handle(self, command: AssignIssues) -> None:
        self.commands.append(command)

        if self._failure is not None:
            raise self._failure
```

The `failure` argument has no default, so every call site states the choice (`IssuesAssigningSpy(failure=None)` for a
succeeding use case, `IssuesAssigningSpy(failure=AssigneesRequired())` for a failing one). `PullRequestsAssigningSpy`
and `PullRequestsAndIssuesAssigningSpy` only record, because no driver test needs them to fail. An inbound `Spy` never
appears in a handler test, because a handler never invokes another handler or inbound port
(`references/unit-test-decision-tree.md`).

## The PyGithub seam (GitHub adapter tests)

A GitHub adapter is the subject. The PyGithub `Repository` it wraps is the only collaborator replaced, by a
`RepositorySpy` that duck-types the members the adapter calls, together with spies for the objects those members
return (`RecordSpy` for an issue or pull request, `UserSpy` for a `NamedUser`). Everything above the seam is real,
the records collaborator (`GitHubIssueRecords`) included, and is what the test covers: whether the adapter reaches
GitHub at all, the filtering of assigned and closed records and of pull requests out of the issue listing, the mapping
of a `NamedUser` to a login, the construction of the domain model, and the translation of a `GithubException`.

Model only the members the adapter touches. A member the adapter does not call stays absent, so an unplanned call fails
with `AttributeError` at the call site instead of passing silently.

```python
# tests/support/spies/repository_spy.py
from typing import final

from github import GithubException

from tests.support.spies.record_spy import RecordSpy
from tests.support.spies.user_spy import UserSpy


@final
class RepositorySpy:

    def __init__(
            self,
            records: tuple[RecordSpy, ...],
            members: tuple[str, ...],
            failure: GithubException | None
    ) -> None:
        self._records = records
        self._members = members
        self._failure = failure
        self.requested = False
        self.listed_assignee: str | None = None

    def get_assignees(self) -> tuple[UserSpy, ...]:
        self._receive_request()
        return tuple(UserSpy(login=member) for member in self._members)

    def get_issues(self, assignee: str) -> tuple[RecordSpy, ...]:
        self._receive_request()
        self.listed_assignee = assignee
        return self._records

    def get_pulls(self) -> tuple[RecordSpy, ...]:
        self._receive_request()
        return self._records

    def get_issue(self, number: int) -> RecordSpy:
        self._receive_request()
        return next(record for record in self._records if record.number == number)

    def get_pull(self, number: int) -> RecordSpy:
        return self.get_issue(number=number)

    def _receive_request(self) -> None:
        self.requested = True

        if self._failure is not None:
            raise self._failure
```

`get_issue` for a number the spy was not seeded with raises `StopIteration`, which is the loud failure an unexpected
call deserves. `get_pulls` and `get_pull` answer from the same records, because `GitHubPullRequests` reads the same
attributes `GitHubIssues` does. Every member funnels through `_receive_request`, so one seeded `failure` fails any call
and `requested` proves whether a call was made at all. `listed_assignee` records the assignee filter of the issue
listing (`GitHubIssueRecords` asks for `'none'`).

The object spies live in their own modules. They carry the attributes the adapter reads and record the writes it
makes:

```python
# tests/support/spies/user_spy.py
from typing import final


@final
class UserSpy:

    def __init__(self, login: str) -> None:
        self.login = login
```

```python
# tests/support/spies/record_spy.py
from typing import final

from tests.support.spies.user_spy import UserSpy


@final
class RecordSpy:

    def __init__(
            self,
            user: UserSpy,
            draft: bool,
            state: str,
            number: int,
            assignees: tuple[UserSpy, ...],
            pull_request: object | None
    ) -> None:
        self.user = user
        self.draft = draft
        self.state = state
        self.number = number
        self.assignees = assignees
        self.pull_request = pull_request
        self.added_assignees: list[str] = []

    def add_to_assignees(self, *logins: str) -> None:
        self.added_assignees.extend(logins)
        self.assignees = (*self.assignees, *(UserSpy(login=login) for login in logins))
```

GitHub lists pull requests in the issue listing and marks them through `pull_request`. The spy models that marker with
the narrowest value the adapter reads. The adapter only checks it against `None`, so a test marks a pull request with
`pull_request=object()`. `state` is the lifecycle marker the adapter keeps open (`'open'`). `user` is the author the
adapter promotes into `Login`, and `draft` is the flag `GitHubPullRequests` copies onto the model (`GitHubIssues`
ignores it, so issue records pass `draft=False`). `add_to_assignees` also appends a `UserSpy` per login, because the
adapter reads `record.assignees` after the write to record the `JournalEntry`. `UserSpy` carries a single
`login: str`.

## Exercise the adapter, then assert

Assert, in separate `# Then` and `# And` blocks:

1. **The returned value**, as domain models compared by value.
2. **The calls the adapter made**, read off the spy: whether a request reached the repository (`requested`), the
   assignees added (`added_assignees`), and what the real `AssignmentJournal` recorded.
3. **The translation**, in its own test (one `# When` per test): a `GithubException` raised by the spy surfaces as
   `GitHubRequestFailed`, the typed exception `src/driven/github` owns, chained with `from`. The shape is in
   `references/exception-assertion.md` § Asserting a translation and its cause.

### Listing (returned value)

```python
def test_unassigned_when_repository_has_mixed_records_then_returns_only_unassigned_issues() -> None:
    # Given a repository with an unassigned issue, an assigned issue, and an unassigned pull request
    repository = RepositorySpy(
        records=(
            RecordSpy(user=UserSpy(login='eve'), draft=False, state='open', number=1, assignees=(), pull_request=None),
            RecordSpy(
                user=UserSpy(login='eve'),
                draft=False,
                state='open',
                number=2,
                assignees=(UserSpy(login='alice'),),
                pull_request=None
            ),
            RecordSpy(
                user=UserSpy(login='eve'),
                draft=False,
                state='open',
                number=3,
                assignees=(),
                pull_request=object()
            )
        ),
        members=(),
        failure=None
    )

    # When the unassigned issues are listed
    issues = issues_over(journal=AssignmentJournal(), repository=repository, triggering_numbers=None).unassigned()

    # Then only the unassigned issue is returned
    assert issues == (Issue(number=1, author=Login(value='eve'), assignees=Logins.empty()),)
```

`issues_over` is a module-level helper that composes the adapter over its records collaborator and a real
`AssignmentJournal`, because the adapter is built from real objects and the repetition belongs in one place:

```python
def issues_over(
        journal: AssignmentJournal,
        repository: RepositorySpy,
        triggering_numbers: tuple[int, ...] | None
) -> GitHubIssues:
    return GitHubIssues(
        records=GitHubIssueRecords(repository=repository, triggering_numbers=triggering_numbers),
        journal=journal,
        repository=repository
    )
```

An empty twin seeds `records=()` and asserts `()`. An empty result means "nothing found", and only the failure twin may
prove the call failed. A twin seeds a closed record and asserts it is left out. The event scope belongs to the records
collaborator, so its twins live in `tests/driven/github/test_github_issue_records.py`: `triggering_numbers=None` scans
the repository for unassigned records (asserting `listed_assignee == 'none'`), `triggering_numbers=(2,)` lists only
record 2, and `triggering_numbers=()` lists nothing.

### Writing (the recorded write)

```python
def test_assign_when_issue_has_assignees_then_they_are_added_to_the_record() -> None:
    # Given a repository with one issue
    record = RecordSpy(user=UserSpy(login='eve'), draft=False, state='open', number=1, assignees=(), pull_request=None)

    # When the issue is assigned to alice and bob
    issues_over(
        journal=AssignmentJournal(),
        repository=RepositorySpy(records=(record,), members=(), failure=None),
        triggering_numbers=None
    ).assign(issue=Issue(number=1, author=Login(value='eve'), assignees=Logins.from_raw(values=('alice', 'bob'))))

    # Then the record receives both assignees
    assert record.added_assignees == ['alice', 'bob']
```

Its guard twin (`test_assign_when_issue_has_no_assignees_then_the_record_is_untouched`) seeds a repository that fails
any request, assigns an issue without assignees, and asserts `repository.requested is False`, proving no call left the
adapter, and that the journal recorded nothing (`journal.issues()` and `journal.pull_requests()` are empty). A journal twin seeds a record that already holds
an assignee and asserts `journal.summary()` lists every assignee the record holds after the write.

## Typing the seam under `mypy --strict`

`mypy --strict` checks `tests/` as well. A duck-typed `RepositorySpy` passed where the adapter annotates the PyGithub
`Repository` class is an `arg-type` error at the call site. `# type: ignore` there is prohibited
(`rules/python-code-style.md` § Analyzer suppressions). The admitted resolutions are a production or configuration
decision, not a test-writing one:

- the adapter annotates the narrowest structural type it reads (a `typing.Protocol` owned by `src/driven/github`
  naming only the members the adapters call), which the spy satisfies without inheriting, or
- the gap is declared once in `pyproject.toml` under `[[tool.mypy.overrides]]`, scoped to the adapter test modules,
  with the comment that justifies it.

This repository chose the second. The override is scoped to `tests.driven.github.*` and disables `arg-type` only, so
the adapters keep their PyGithub `Repository` annotation and every other check still runs on those tests:

```toml
[[tool.mypy.overrides]]
# The driven adapter tests hand a duck-typed RepositorySpy where PyGithub annotates its concrete Repository.
module = ["tests.driven.github.*"]
disable_error_code = ["arg-type"]
```

A new test module under `tests/driven/github/` is covered by it. A duck-typed seam anywhere else needs the same
decision taken again, so stop and raise it in the change summary instead of choosing silently. Never inherit the spy
from the PyGithub class: a concrete class extends only an `ABC` port or an exception base.

## pytest fixtures for spies

A `@pytest.fixture` is admitted for a boundary double that needs setup shared by several tests of a module. It is
function scoped (the default), so each test receives a fresh spy, and it is named for the business concept
(`repository`), never `repository_fixture`. A spy is never `scope='module'` or `scope='session'`: it records, and a
shared recorder couples the tests.

## The environment boundary (`ActionSettings` tests)

The process environment is the boundary of the environment adapter, and `ActionSettings.from_environment` receives it
as a `Mapping[str, str]` parameter instead of reading `os.environ` itself. Only `src/main.py` passes `os.environ`. A
test therefore hands in a plain `dict` and patches nothing. `monkeypatch.setattr`, `monkeypatch.setitem` on
`os.environ`, and `unittest.mock.patch.dict` are the patching the rule prohibits, and `monkeypatch.setenv` has no seam
to reach.

A module-level constant holds the required inputs, never mutated, and a missing-input test derives its variant from
it with a `dict` expression. The optional inputs are left out of the baseline, so the first test proves they take
the defaults `action.yml` declares, and the missing-input tests assert that every absent input is named at once:

```python
import pytest

from src.driven.environment.action_settings import ActionSettings
from src.driven.environment.assignment_preferences import AssignmentPreferences
from src.driven.environment.missing_action_input import MissingActionInput
from src.driven.environment.triggering_event import TriggeringEvent

REQUIRED_INPUTS = {
    'GITHUB_ACTOR': 'octocat',
    'INPUT_ASSIGNEES': ' alice , bob,, ',
    'GITHUB_REPOSITORY': 'octocat/hello-world',
    'INPUT_GITHUB_TOKEN': 'placeholder-token'
}


def test_from_environment_when_only_required_inputs_are_present_then_optional_inputs_take_their_defaults() -> None:
    # When the settings are read from an environment holding only the required inputs
    settings = ActionSettings.from_environment(environment=REQUIRED_INPUTS)

    # Then every input is parsed, and the optional ones take the defaults declared in action.yml
    assert settings == ActionSettings(
        actor='octocat',
        event=TriggeringEvent.repository_scan(),
        assignees=('alice', 'bob'),
        repository='octocat/hello-world',
        preferences=AssignmentPreferences(
            skip_bots=False,
            skip_drafts=False,
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        ),
        github_token='placeholder-token',
        assignment_options=('ISSUE',)
    )


@pytest.mark.parametrize(
    ids=['actor absent', 'repository absent', 'assignees absent', 'token absent', 'assignees blank'],
    argnames=['environment', 'missing'],
    argvalues=[
        ({key: value for key, value in REQUIRED_INPUTS.items() if key != 'GITHUB_ACTOR'}, ('GITHUB_ACTOR',)),
        (
            {key: value for key, value in REQUIRED_INPUTS.items() if key != 'GITHUB_REPOSITORY'},
            ('GITHUB_REPOSITORY',)
        ),
        ({key: value for key, value in REQUIRED_INPUTS.items() if key != 'INPUT_ASSIGNEES'}, ('INPUT_ASSIGNEES',)),
        (
            {key: value for key, value in REQUIRED_INPUTS.items() if key != 'INPUT_GITHUB_TOKEN'},
            ('INPUT_GITHUB_TOKEN',)
        ),
        ({**REQUIRED_INPUTS, 'INPUT_ASSIGNEES': '  '}, ('INPUT_ASSIGNEES',))
    ]
)
def test_from_environment_when_a_required_input_is_missing_then_missing_action_input_names_it(
        missing: tuple[str, ...],
        environment: dict[str, str]
) -> None:
    # Then reading fails because a required input is missing
    with pytest.raises(MissingActionInput) as failure:
        # When the settings are read without that input
        ActionSettings.from_environment(environment=environment)

    # And the failure names that input
    assert failure.value.variables == missing


def test_from_environment_when_every_required_input_is_missing_then_missing_action_input_names_them_all() -> None:
    # Then reading fails because the required inputs are missing
    with pytest.raises(MissingActionInput) as failure:
        # When the settings are read from an empty environment
        ActionSettings.from_environment(environment={})

    # And the failure names every required input at once
    assert failure.value.variables == ('GITHUB_ACTOR', 'GITHUB_REPOSITORY', 'INPUT_ASSIGNEES', 'INPUT_GITHUB_TOKEN')
```

The boolean inputs and the assignment options each get the same treatment when a new promotion rule lands: one
parameterized test per promotion, covering the accepted values and the rejected one.

## Anti-patterns

- **Doubling inside the hexagon.** A `Spy` of `Issue`, of `Logins`, or of a command tests nothing. Use the real
  object.
- **Doubling the subject.** A `Spy` of `GitHubIssues` in a `GitHubIssues` test, or of the `Issues` port there. Double
  the port when testing the handler that consumes it, never when testing the adapter that implements it.
- **`MagicMock(spec=Repository)` or `patch('github.Repository...')`.** Prohibited by the rule. A hand-written
  `RepositorySpy` states exactly which members the adapter uses.
- **A spy with behavior.** Filtering, sorting, or deciding in the spy moves logic out of the code under test. Seed the
  spy with the answer instead.
- **A silent default.** A spy that returns `None` or `()` for an unseeded call hides an unexpected request. Let the
  lookup raise.
- **Asserting only the outcome, or only the calls.** A correct model reached through the wrong call, or a correct call
  whose answer never shaped the result, both pass a half-written test. Assert both.
- **Relying on the ambient environment.** A settings test that reads `os.environ` passes only because the runner or
  `.env.development` happens to define an input. Hand `from_environment` a `dict` that states every input instead.
