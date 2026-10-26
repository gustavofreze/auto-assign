import pytest
from github import GithubException

from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.issue import Issue
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_issue_records import GitHubIssueRecords
from src.driven.github.github_issues import GitHubIssues
from src.driven.github.github_request_failed import GitHubRequestFailed
from tests.support.spies.record_spy import RecordSpy
from tests.support.spies.repository_spy import RepositorySpy
from tests.support.spies.user_spy import UserSpy


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


def test_unassigned_when_a_bot_opened_an_issue_then_the_issue_carries_its_author() -> None:
    # Given a repository with an unassigned issue a bot opened
    repository = RepositorySpy(
        records=(
            RecordSpy(
                user=UserSpy(login='dependabot[bot]'),
                draft=False,
                state='open',
                number=5,
                assignees=(),
                pull_request=None
            ),
        ),
        members=(),
        failure=None
    )

    # When the unassigned issues are listed
    issues = issues_over(journal=AssignmentJournal(), repository=repository, triggering_numbers=None).unassigned()

    # Then the issue carries the bot as its author
    assert issues == (Issue(number=5, author=Login(value='dependabot[bot]'), assignees=Logins.empty()),)


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


def test_assign_when_issue_is_assigned_then_the_journal_records_the_assignees_held_afterwards() -> None:
    # Given a repository whose issue gained dave as an assignee since it was listed
    record = RecordSpy(
        user=UserSpy(login='eve'),
        draft=False,
        state='open',
        number=1,
        assignees=(UserSpy(login='dave'),),
        pull_request=None
    )

    # And an empty journal
    journal = AssignmentJournal()

    # When the issue is assigned to alice
    issues_over(
        journal=journal,
        repository=RepositorySpy(records=(record,), members=(), failure=None),
        triggering_numbers=None
    ).assign(issue=Issue(number=1, author=Login(value='eve'), assignees=Logins.from_raw(values=('alice',))))

    # Then the journal records every assignee the issue holds after the assignment
    assert journal.summary() == (
        '### Auto assign\n\n'
        '| Item | Assignees |\n'
        '|:-----|:----------|\n'
        '| Issue #1 | dave, alice |\n'
    )


def test_assign_when_issue_has_no_assignees_then_the_record_is_untouched() -> None:
    # Given a repository that fails any request
    repository = RepositorySpy(records=(), members=(), failure=GithubException(status=500))

    # And an empty journal
    journal = AssignmentJournal()

    # When an issue without assignees is assigned
    issues_over(journal=journal, repository=repository, triggering_numbers=None).assign(
        issue=Issue(number=1, author=Login(value='eve'), assignees=Logins.empty())
    )

    # Then no request reaches the repository
    assert repository.requested is False

    # And nothing is recorded in the journal
    assert (journal.issues(), journal.pull_requests()) == ([], [])


def test_unassigned_when_github_fails_then_github_request_failed_is_raised() -> None:
    # Given a repository that fails any request
    issues = issues_over(
        journal=AssignmentJournal(),
        repository=RepositorySpy(records=(), members=(), failure=GithubException(status=502)),
        triggering_numbers=None
    )

    # Then the listing fails with the translated failure
    with pytest.raises(GitHubRequestFailed):
        # When the unassigned issues are listed
        issues.unassigned()


def test_assign_when_github_fails_then_github_request_failed_is_raised() -> None:
    # Given a repository that fails any request
    issues = issues_over(
        journal=AssignmentJournal(),
        repository=RepositorySpy(records=(), members=(), failure=GithubException(status=403)),
        triggering_numbers=None
    )

    # Then the assignment fails with the translated failure
    with pytest.raises(GitHubRequestFailed):
        # When an issue with assignees is assigned
        issues.assign(issue=Issue(number=1, author=Login(value='eve'), assignees=Logins.from_raw(values=('alice',))))


def test_unassigned_when_an_issue_triggered_the_run_then_returns_only_that_issue() -> None:
    # Given a repository with two unassigned issues
    repository = RepositorySpy(
        records=(
            RecordSpy(user=UserSpy(login='eve'), draft=False, state='open', number=1, assignees=(), pull_request=None),
            RecordSpy(user=UserSpy(login='dave'), draft=False, state='open', number=2, assignees=(), pull_request=None)
        ),
        members=(),
        failure=None
    )

    # When the unassigned issues are listed for the run triggered by issue 2
    issues = issues_over(journal=AssignmentJournal(), repository=repository, triggering_numbers=(2,)).unassigned()

    # Then only the triggering issue is returned
    assert issues == (Issue(number=2, author=Login(value='dave'), assignees=Logins.empty()),)


def test_unassigned_when_a_pull_request_triggered_the_run_then_no_issue_is_listed() -> None:
    # Given a repository that fails any request
    repository = RepositorySpy(records=(), members=(), failure=GithubException(status=500))

    # When the unassigned issues are listed for a run no issue triggered
    issues = issues_over(journal=AssignmentJournal(), repository=repository, triggering_numbers=()).unassigned()

    # Then no issue is returned
    assert not issues

    # And no request reaches the repository
    assert repository.requested is False


def test_unassigned_when_a_closed_issue_triggered_the_run_then_no_issue_is_listed() -> None:
    # Given a repository whose triggering issue is closed
    repository = RepositorySpy(
        records=(
            RecordSpy(
                user=UserSpy(login='eve'),
                draft=False,
                state='closed',
                number=4,
                assignees=(),
                pull_request=None
            ),
        ),
        members=(),
        failure=None
    )

    # When the unassigned issues are listed for the run triggered by issue 4
    issues = issues_over(journal=AssignmentJournal(), repository=repository, triggering_numbers=(4,)).unassigned()

    # Then no issue is returned
    assert not issues
