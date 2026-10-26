import pytest

from src.application.domain.exceptions.assignees_required import AssigneesRequired
from src.application.domain.exceptions.self_assignment_not_allowed import SelfAssignmentNotAllowed
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.issue import Issue
from tests.support.builders.assignment_builder import AssignmentBuilder


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


def test_assign_when_no_assignee_is_given_and_empty_assignment_is_allowed_then_issue_stays_unassigned() -> None:
    # Given an issue without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the issue is assigned to nobody while an empty assignment is allowed
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.empty())
        .with_allow_no_assignees(allow_no_assignees=True)
        .build()
    )

    # Then the issue stays without assignees
    assert not assigned_issue.assignees


def test_assign_when_actor_assigns_itself_and_self_assignment_is_denied_then_it_is_refused() -> None:
    # Given an issue without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # Then the assignment fails because the actor would assign itself
    with pytest.raises(SelfAssignmentNotAllowed):
        # When the actor assigns the issue to itself while self-assignment and an empty assignment are denied
        issue.assign(
            assignment=AssignmentBuilder.new()
            .with_actor(actor=Login(value='octocat'))
            .with_assignees(assignees=Logins.from_raw(values=('octocat',)))
            .with_allow_self_assign(allow_self_assign=False)
            .with_allow_no_assignees(allow_no_assignees=False)
            .build()
        )


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


@pytest.mark.parametrize(
    ids=['actor among others', 'actor alone'],
    argnames=['assignees', 'granted'],
    argvalues=[
        (Logins.from_raw(values=('octocat', 'alice')), Logins.from_raw(values=('alice',))),
        (Logins.from_raw(values=('octocat',)), Logins.empty())
    ]
)
def test_assign_when_self_assignment_is_denied_and_empty_assignment_is_allowed_then_actor_is_left_out(
        granted: Logins,
        assignees: Logins
) -> None:
    # Given an issue without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the actor is among the assignees while self-assignment is denied and an empty assignment is allowed
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_actor(actor=Login(value='octocat'))
        .with_assignees(assignees=assignees)
        .with_allow_self_assign(allow_self_assign=False)
        .with_allow_no_assignees(allow_no_assignees=True)
        .build()
    )

    # Then every assignee except the actor is granted
    assert assigned_issue.assignees == granted


def test_assign_when_the_author_is_assigned_then_the_author_follows_the_assignees() -> None:
    # Given an issue opened by carol without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the issue is assigned to alice and to its author
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.from_raw(values=('alice',)))
        .with_assign_author(assign_author=True)
        .build()
    )

    # Then the issue carries alice followed by carol
    assert assigned_issue.assignees == Logins.from_raw(values=('alice', 'carol'))


def test_assign_when_only_the_author_is_assigned_and_empty_assignment_is_denied_then_the_author_is_granted() -> None:
    # Given an issue opened by carol without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the issue is assigned to its author alone while an empty assignment is denied
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.empty())
        .with_assign_author(assign_author=True)
        .with_allow_no_assignees(allow_no_assignees=False)
        .build()
    )

    # Then the issue carries carol only
    assert assigned_issue.assignees == Logins.from_raw(values=('carol',))


def test_assign_when_self_assignment_leaves_the_actor_out_and_the_author_is_assigned_then_author_is_added() -> None:
    # Given an issue opened by carol without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the actor and alice are requested with the author while self-assignment is denied
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_actor(actor=Login(value='octocat'))
        .with_assignees(assignees=Logins.from_raw(values=('octocat', 'alice')))
        .with_assign_author(assign_author=True)
        .with_allow_self_assign(allow_self_assign=False)
        .with_allow_no_assignees(allow_no_assignees=True)
        .build()
    )

    # Then the actor is left out and carol follows alice
    assert assigned_issue.assignees == Logins.from_raw(values=('alice', 'carol'))


def test_assign_when_a_bot_opened_the_issue_and_bots_are_skipped_then_the_issue_stays_unchanged() -> None:
    # Given an issue opened by a bot without assignees
    issue = Issue(number=1, author=Login(value='dependabot[bot]'), assignees=Logins.empty())

    # When the issue is assigned to two members while bots are skipped
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.from_raw(values=('alice', 'bob')))
        .with_eligibility(eligibility=Eligibility(skip_bots=True, skip_drafts=False))
        .build()
    )

    # Then the issue stays without assignees
    assert assigned_issue == Issue(number=1, author=Login(value='dependabot[bot]'), assignees=Logins.empty())


def test_assign_when_drafts_are_skipped_then_the_issue_is_still_assigned() -> None:
    # Given an issue opened by carol without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # When the issue is assigned to alice while drafts are skipped
    assigned_issue = issue.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.from_raw(values=('alice',)))
        .with_eligibility(eligibility=Eligibility(skip_bots=False, skip_drafts=True))
        .build()
    )

    # Then the issue carries alice, since an issue is never a draft
    assert assigned_issue.assignees == Logins.from_raw(values=('alice',))
