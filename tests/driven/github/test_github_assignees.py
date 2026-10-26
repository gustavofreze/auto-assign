import pytest
from github import GithubException

from src.application.domain.models.commons.logins import Logins
from src.driven.github.github_assignees import GitHubAssignees
from src.driven.github.github_request_failed import GitHubRequestFailed
from tests.support.spies.repository_spy import RepositorySpy


def test_assignable_when_some_logins_are_members_then_returns_only_members_in_requested_order() -> None:
    # Given a repository whose members are alice and bob
    assignees = GitHubAssignees(repository=RepositorySpy(records=(), members=('alice', 'bob'), failure=None))

    # When bob, a stranger, and alice are requested
    assignable = assignees.assignable(logins=Logins.from_raw(values=('bob', 'stranger', 'alice')))

    # Then only the members are returned, in the requested order
    assert assignable == Logins.from_raw(values=('bob', 'alice'))


def test_assignable_when_github_fails_then_github_request_failed_is_raised() -> None:
    # Given a repository that fails any request
    assignees = GitHubAssignees(repository=RepositorySpy(records=(), members=(), failure=GithubException(status=500)))

    # Then the lookup fails with the translated failure instead of an empty selection
    with pytest.raises(GitHubRequestFailed):
        # When the assignable logins are requested
        assignees.assignable(logins=Logins.from_raw(values=('alice',)))
