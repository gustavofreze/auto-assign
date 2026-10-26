import pytest

from src.application.commands.assign_issues import AssignIssues
from src.application.domain.exceptions.assignees_required import AssigneesRequired
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
    assignees = AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice',)))
    handler = IssuesAssigningHandler(issues=issues, assignees=assignees)

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

    # And the repository was asked about every requested assignee
    assert assignees.requested_logins == [Logins.from_raw(values=('alice', 'stranger'))]


def test_handle_when_no_issue_is_unassigned_then_nothing_is_assigned() -> None:
    # Given no unassigned issue
    issues = IssuesSpy(unassigned_issues=())

    # And a repository without members
    assignees = AssigneesSpy(assignable_logins=Logins.empty())
    handler = IssuesAssigningHandler(issues=issues, assignees=assignees)

    # When the issues are assigned to a stranger
    handler.handle(
        command=AssignIssues(
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
    assert not issues.assigned_issues

    # And the repository is not asked about the assignees
    assert not assignees.requested_logins


def test_handle_when_no_requested_assignee_is_accepted_then_assignees_required_is_raised() -> None:
    # Given one unassigned issue
    issues = IssuesSpy(unassigned_issues=(Issue(number=1, author=Login(value='carol'), assignees=Logins.empty()),))

    # And a repository that accepts none of the requested assignees
    handler = IssuesAssigningHandler(issues=issues, assignees=AssigneesSpy(assignable_logins=Logins.empty()))

    # Then the assignment fails because no assignee remains
    with pytest.raises(AssigneesRequired):
        # When the issue is assigned to a stranger
        handler.handle(
            command=AssignIssues(
                actor='octocat',
                assignees=('stranger',),
                skip_bots=False,
                skip_drafts=False,
                assign_author=False,
                allow_self_assign=True,
                allow_no_assignees=False
            )
        )


def test_handle_when_bots_are_skipped_then_the_issue_a_bot_opened_keeps_no_assignee() -> None:
    # Given an unassigned issue opened by a bot and one opened by carol
    issues = IssuesSpy(
        unassigned_issues=(
            Issue(number=1, author=Login(value='dependabot[bot]'), assignees=Logins.empty()),
            Issue(number=2, author=Login(value='carol'), assignees=Logins.empty())
        )
    )

    # And a repository that accepts alice
    handler = IssuesAssigningHandler(
        issues=issues,
        assignees=AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice',)))
    )

    # When the issues are assigned to alice while bots are skipped
    handler.handle(
        command=AssignIssues(
            actor='octocat',
            assignees=('alice',),
            skip_bots=True,
            skip_drafts=False,
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then only the issue carol opened is assigned to alice
    assert issues.assigned_issues == [
        Issue(number=1, author=Login(value='dependabot[bot]'), assignees=Logins.empty()),
        Issue(number=2, author=Login(value='carol'), assignees=Logins.from_raw(values=('alice',)))
    ]


def test_handle_when_the_author_is_assigned_then_each_issue_also_carries_its_author() -> None:
    # Given unassigned issues opened by carol and by dave
    issues = IssuesSpy(
        unassigned_issues=(
            Issue(number=1, author=Login(value='carol'), assignees=Logins.empty()),
            Issue(number=2, author=Login(value='dave'), assignees=Logins.empty())
        )
    )

    # And a repository that accepts alice
    handler = IssuesAssigningHandler(
        issues=issues,
        assignees=AssigneesSpy(assignable_logins=Logins.from_raw(values=('alice',)))
    )

    # When the issues are assigned to alice and to their authors
    handler.handle(
        command=AssignIssues(
            actor='octocat',
            assignees=('alice',),
            skip_bots=False,
            skip_drafts=False,
            assign_author=True,
            allow_self_assign=True,
            allow_no_assignees=False
        )
    )

    # Then each issue carries alice followed by its author
    assert issues.assigned_issues == [
        Issue(number=1, author=Login(value='carol'), assignees=Logins.from_raw(values=('alice', 'carol'))),
        Issue(number=2, author=Login(value='dave'), assignees=Logins.from_raw(values=('alice', 'dave')))
    ]
