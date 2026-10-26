from src.application.commands.assign_pull_requests_and_issues import AssignPullRequestsAndIssues
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.issue import Issue
from src.application.domain.models.pull_request import PullRequest
from src.application.handlers.pull_requests_and_issues_assigning_handler import PullRequestsAndIssuesAssigningHandler
from tests.support.spies.assignees_spy import AssigneesSpy
from tests.support.spies.issues_spy import IssuesSpy
from tests.support.spies.pull_requests_spy import PullRequestsSpy


def test_handle_when_pull_requests_and_issues_are_unassigned_then_both_are_assigned() -> None:
    # Given an unassigned issue and an unassigned pull request
    issues = IssuesSpy(unassigned_issues=(Issue(number=1, author=Login(value='carol'), assignees=Logins.empty()),))
    pull_requests = PullRequestsSpy(
        unassigned_pull_requests=(
            PullRequest(number=7, draft=False, author=Login(value='carol'), assignees=Logins.empty()),
        )
    )

    # And a repository that accepts alice
    assignees = AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice',)))
    handler = PullRequestsAndIssuesAssigningHandler(issues=issues, assignees=assignees, pull_requests=pull_requests)

    # When pull requests and issues are assigned to alice
    handler.handle(
        command=AssignPullRequestsAndIssues(
            actor='octocat',
            assignees=('alice',),
            skip_bots=False,
            skip_drafts=False,
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then the pull request is assigned to alice
    assert pull_requests.assigned_pull_requests == [
        PullRequest(number=7, draft=False, author=Login(value='carol'), assignees=Logins.from_raw(values=('alice',)))
    ]

    # And the issue is assigned to alice
    assert issues.assigned_issues == [
        Issue(number=1, author=Login(value='carol'), assignees=Logins.from_raw(values=('alice',)))
    ]

    # And the repository was asked about the assignees once for both kinds
    assert assignees.requested_logins == [Logins.from_raw(values=('alice',))]


def test_handle_when_nothing_is_unassigned_then_nothing_is_assigned() -> None:
    # Given no unassigned issue and no unassigned pull request
    issues = IssuesSpy(unassigned_issues=())
    pull_requests = PullRequestsSpy(unassigned_pull_requests=())

    # And a repository without members
    assignees = AssigneesSpy(assignable_logins=Logins.empty())
    handler = PullRequestsAndIssuesAssigningHandler(issues=issues, assignees=assignees, pull_requests=pull_requests)

    # When pull requests and issues are assigned to a stranger
    handler.handle(
        command=AssignPullRequestsAndIssues(
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
    assert (pull_requests.assigned_pull_requests, issues.assigned_issues) == ([], [])

    # And the repository is not asked about the assignees
    assert not assignees.requested_logins


def test_handle_when_bots_and_drafts_are_skipped_then_only_eligible_items_carry_the_assignees_and_authors() -> None:
    # Given an issue a bot opened, an issue carol opened, a draft, and a ready pull request
    issues = IssuesSpy(
        unassigned_issues=(
            Issue(number=1, author=Login(value='dependabot[bot]'), assignees=Logins.empty()),
            Issue(number=2, author=Login(value='carol'), assignees=Logins.empty())
        )
    )
    pull_requests = PullRequestsSpy(
        unassigned_pull_requests=(
            PullRequest(number=7, draft=True, author=Login(value='dave'), assignees=Logins.empty()),
            PullRequest(number=8, draft=False, author=Login(value='dave'), assignees=Logins.empty())
        )
    )

    # And a repository that accepts alice
    handler = PullRequestsAndIssuesAssigningHandler(
        issues=issues,
        assignees=AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice',))),
        pull_requests=pull_requests
    )

    # When everything is assigned to alice and to its author while bots and drafts are skipped
    handler.handle(
        command=AssignPullRequestsAndIssues(
            actor='octocat',
            assignees=('alice',),
            skip_bots=True,
            skip_drafts=True,
            assign_author=True,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then only the ready pull request carries alice and its author
    assert pull_requests.assigned_pull_requests == [
        PullRequest(number=7, draft=True, author=Login(value='dave'), assignees=Logins.empty()),
        PullRequest(
            number=8,
            draft=False,
            author=Login(value='dave'),
            assignees=Logins.from_raw(values=('alice', 'dave'))
        )
    ]

    # And only the issue carol opened carries alice and its author
    assert issues.assigned_issues == [
        Issue(number=1, author=Login(value='dependabot[bot]'), assignees=Logins.empty()),
        Issue(number=2, author=Login(value='carol'), assignees=Logins.from_raw(values=('alice', 'carol')))
    ]
