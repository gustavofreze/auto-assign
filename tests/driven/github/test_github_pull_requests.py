import pytest
from github import GithubException

from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.pull_request import PullRequest
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_pull_request_records import GitHubPullRequestRecords
from src.driven.github.github_pull_requests import GitHubPullRequests
from src.driven.github.github_request_failed import GitHubRequestFailed
from tests.support.spies.record_spy import RecordSpy
from tests.support.spies.repository_spy import RepositorySpy
from tests.support.spies.user_spy import UserSpy


def pull_requests_over(
        journal: AssignmentJournal,
        repository: RepositorySpy,
        triggering_numbers: tuple[int, ...] | None
) -> GitHubPullRequests:
    return GitHubPullRequests(
        records=GitHubPullRequestRecords(repository=repository, triggering_numbers=triggering_numbers),
        journal=journal,
        repository=repository
    )


def test_unassigned_when_repository_has_mixed_records_then_returns_only_unassigned_pull_requests() -> None:
    # Given a repository with an unassigned and an assigned pull request
    repository = RepositorySpy(
        records=(
            RecordSpy(user=UserSpy(login='eve'), draft=False, state='open', number=7, assignees=(), pull_request=None),
            RecordSpy(
                user=UserSpy(login='eve'),
                draft=False,
                state='open',
                number=8,
                assignees=(UserSpy(login='alice'),),
                pull_request=None
            )
        ),
        members=(),
        failure=None
    )

    # When the unassigned pull requests are listed
    pull_requests = pull_requests_over(
        journal=AssignmentJournal(),
        repository=repository,
        triggering_numbers=None
    ).unassigned()

    # Then only the unassigned pull request is returned
    assert pull_requests == (PullRequest(number=7, draft=False, author=Login(value='eve'), assignees=Logins.empty()),)


def test_unassigned_when_a_draft_is_open_then_it_is_listed_with_its_draft_flag_and_author() -> None:
    # Given a repository with an unassigned draft that dave opened
    repository = RepositorySpy(
        records=(
            RecordSpy(user=UserSpy(login='dave'), draft=True, state='open', number=7, assignees=(), pull_request=None),
        ),
        members=(),
        failure=None
    )

    # When the unassigned pull requests are listed
    pull_requests = pull_requests_over(
        journal=AssignmentJournal(),
        repository=repository,
        triggering_numbers=None
    ).unassigned()

    # Then the draft is returned as a draft opened by dave
    assert pull_requests == (PullRequest(number=7, draft=True, author=Login(value='dave'), assignees=Logins.empty()),)


def test_assign_when_pull_request_has_assignees_then_they_are_added_to_the_record() -> None:
    # Given a repository with one pull request
    record = RecordSpy(user=UserSpy(login='eve'), draft=False, state='open', number=7, assignees=(), pull_request=None)

    # When the pull request is assigned to alice
    pull_requests_over(
        journal=AssignmentJournal(),
        repository=RepositorySpy(records=(record,), members=(), failure=None),
        triggering_numbers=None
    ).assign(
        pull_request=PullRequest(
            number=7,
            draft=False,
            author=Login(value='eve'),
            assignees=Logins.from_raw(values=('alice',))
        )
    )

    # Then the record receives the assignee
    assert record.added_assignees == ['alice']


def test_assign_when_pull_request_is_assigned_then_the_journal_records_the_assignees_held_afterwards() -> None:
    # Given a repository whose pull request gained dave as an assignee since it was listed
    record = RecordSpy(
        user=UserSpy(login='eve'),
        draft=False,
        state='open',
        number=7,
        assignees=(UserSpy(login='dave'),),
        pull_request=None
    )

    # And an empty journal
    journal = AssignmentJournal()

    # When the pull request is assigned to alice and bob
    pull_requests_over(
        journal=journal,
        repository=RepositorySpy(records=(record,), members=(), failure=None),
        triggering_numbers=None
    ).assign(
        pull_request=PullRequest(
            number=7,
            draft=False,
            author=Login(value='eve'),
            assignees=Logins.from_raw(values=('alice', 'bob'))
        )
    )

    # Then the journal records every assignee the pull request holds after the assignment
    assert journal.summary() == (
        '### Auto assign\n\n'
        '| Item | Assignees |\n'
        '|:-----|:----------|\n'
        '| Pull request #7 | dave, alice, bob |\n'
    )


def test_assign_when_pull_request_has_no_assignees_then_the_record_is_untouched() -> None:
    # Given a repository that fails any request
    repository = RepositorySpy(records=(), members=(), failure=GithubException(status=500))

    # And an empty journal
    journal = AssignmentJournal()

    # When a pull request without assignees is assigned
    pull_requests_over(journal=journal, repository=repository, triggering_numbers=None).assign(
        pull_request=PullRequest(number=7, draft=False, author=Login(value='eve'), assignees=Logins.empty())
    )

    # Then no request reaches the repository
    assert repository.requested is False

    # And nothing is recorded in the journal
    assert (journal.issues(), journal.pull_requests()) == ([], [])


def test_unassigned_when_github_fails_then_github_request_failed_is_raised() -> None:
    # Given a repository that fails any request
    pull_requests = pull_requests_over(
        journal=AssignmentJournal(),
        repository=RepositorySpy(records=(), members=(), failure=GithubException(status=502)),
        triggering_numbers=None
    )

    # Then the listing fails with the translated failure
    with pytest.raises(GitHubRequestFailed):
        # When the unassigned pull requests are listed
        pull_requests.unassigned()


def test_assign_when_github_fails_then_github_request_failed_is_raised() -> None:
    # Given a repository that fails any request
    pull_requests = pull_requests_over(
        journal=AssignmentJournal(),
        repository=RepositorySpy(records=(), members=(), failure=GithubException(status=403)),
        triggering_numbers=None
    )

    # Then the assignment fails with the translated failure
    with pytest.raises(GitHubRequestFailed):
        # When a pull request with assignees is assigned
        pull_requests.assign(
            pull_request=PullRequest(
                number=7,
                draft=False,
                author=Login(value='eve'),
                assignees=Logins.from_raw(values=('alice',))
            )
        )


def test_unassigned_when_a_pull_request_triggered_the_run_then_returns_only_that_pull_request() -> None:
    # Given a repository with two unassigned pull requests
    repository = RepositorySpy(
        records=(
            RecordSpy(user=UserSpy(login='eve'), draft=False, state='open', number=7, assignees=(), pull_request=None),
            RecordSpy(user=UserSpy(login='dave'), draft=False, state='open', number=8, assignees=(), pull_request=None)
        ),
        members=(),
        failure=None
    )

    # When the unassigned pull requests are listed for the run triggered by pull request 8
    pull_requests = pull_requests_over(
        journal=AssignmentJournal(),
        repository=repository,
        triggering_numbers=(8,)
    ).unassigned()

    # Then only the triggering pull request is returned
    assert pull_requests == (PullRequest(number=8, draft=False, author=Login(value='dave'), assignees=Logins.empty()),)


def test_unassigned_when_a_closed_pull_request_triggered_the_run_then_no_pull_request_is_listed() -> None:
    # Given a repository whose triggering pull request is closed
    repository = RepositorySpy(
        records=(
            RecordSpy(
                user=UserSpy(login='eve'),
                draft=False,
                state='closed',
                number=9,
                assignees=(),
                pull_request=None
            ),
        ),
        members=(),
        failure=None
    )

    # When the unassigned pull requests are listed for the run triggered by pull request 9
    pull_requests = pull_requests_over(
        journal=AssignmentJournal(),
        repository=repository,
        triggering_numbers=(9,)
    ).unassigned()

    # Then no pull request is returned
    assert not pull_requests
