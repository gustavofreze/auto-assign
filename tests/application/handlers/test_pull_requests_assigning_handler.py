from src.application.commands.assign_pull_requests import AssignPullRequests
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.pull_request import PullRequest
from src.application.handlers.pull_requests_assigning_handler import PullRequestsAssigningHandler
from tests.support.spies.assignees_spy import AssigneesSpy
from tests.support.spies.pull_requests_spy import PullRequestsSpy


def test_handle_when_pull_requests_are_unassigned_then_each_is_assigned_to_the_accepted_assignees() -> None:
    # Given an unassigned pull request
    pull_requests = PullRequestsSpy(
        unassigned_pull_requests=(
            PullRequest(number=7, draft=False, author=Login(value='carol'), assignees=Logins.empty()),
        )
    )

    # And a repository that accepts bob and alice
    handler = PullRequestsAssigningHandler(
        assignees=AssigneesSpy(assignable_logins=Logins.from_raw(values=('bob', 'alice'))),
        pull_requests=pull_requests
    )

    # When the pull requests are assigned to bob and alice
    handler.handle(
        command=AssignPullRequests(
            actor='octocat',
            assignees=('bob', 'alice'),
            skip_bots=False,
            skip_drafts=False,
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then the pull request is assigned to both, in the requested order
    assert pull_requests.assigned_pull_requests == [
        PullRequest(
            number=7,
            draft=False,
            author=Login(value='carol'),
            assignees=Logins.from_raw(values=('bob', 'alice'))
        )
    ]


def test_handle_when_no_pull_request_is_unassigned_then_nothing_is_assigned() -> None:
    # Given no unassigned pull request
    pull_requests = PullRequestsSpy(unassigned_pull_requests=())

    # And a repository without members
    assignees = AssigneesSpy(assignable_logins=Logins.empty())
    handler = PullRequestsAssigningHandler(assignees=assignees, pull_requests=pull_requests)

    # When the pull requests are assigned to a stranger
    handler.handle(
        command=AssignPullRequests(
            actor='octocat',
            assignees=('stranger',),
            skip_bots=False,
            skip_drafts=False,
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then nothing is assigned
    assert not pull_requests.assigned_pull_requests

    # And the repository is not asked about the assignees
    assert not assignees.requested_logins


def test_handle_when_drafts_are_skipped_then_the_draft_keeps_no_assignee() -> None:
    # Given an unassigned draft and an unassigned ready pull request
    pull_requests = PullRequestsSpy(
        unassigned_pull_requests=(
            PullRequest(number=7, draft=True, author=Login(value='carol'), assignees=Logins.empty()),
            PullRequest(number=8, draft=False, author=Login(value='carol'), assignees=Logins.empty())
        )
    )

    # And a repository that accepts alice
    handler = PullRequestsAssigningHandler(
        assignees=AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice',))),
        pull_requests=pull_requests
    )

    # When the pull requests are assigned to alice and to their authors while drafts are skipped
    handler.handle(
        command=AssignPullRequests(
            actor='octocat',
            assignees=('alice',),
            skip_bots=False,
            skip_drafts=True,
            assign_author=True,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then only the ready pull request is assigned to alice and its author
    assert pull_requests.assigned_pull_requests == [
        PullRequest(number=7, draft=True, author=Login(value='carol'), assignees=Logins.empty()),
        PullRequest(
            number=8,
            draft=False,
            author=Login(value='carol'),
            assignees=Logins.from_raw(values=('alice', 'carol'))
        )
    ]
