import pytest

from src.application.domain.exceptions.assignees_required import AssigneesRequired
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.pull_request import PullRequest
from tests.support.builders.assignment_builder import AssignmentBuilder


def test_assign_when_assignees_are_given_then_pull_request_carries_them() -> None:
    # Given a ready pull request opened by carol without assignees
    pull_request = PullRequest(number=7, draft=False, author=Login(value='carol'), assignees=Logins.empty())

    # When the pull request is assigned to one member
    assigned_pull_request = pull_request.assign(
        assignment=AssignmentBuilder.new().with_assignees(assignees=Logins.from_raw(values=('alice',))).build()
    )

    # Then the pull request carries the assignee
    assert assigned_pull_request == PullRequest(
        number=7,
        draft=False,
        author=Login(value='carol'),
        assignees=Logins.from_raw(values=('alice',))
    )


def test_assign_when_no_assignee_is_given_and_empty_assignment_is_denied_then_assignees_required_is_raised() -> None:
    # Given a ready pull request without assignees
    pull_request = PullRequest(number=7, draft=False, author=Login(value='carol'), assignees=Logins.empty())

    # Then the assignment fails because no assignee was given
    with pytest.raises(AssigneesRequired):
        # When the pull request is assigned to nobody while an empty assignment is denied
        pull_request.assign(
            assignment=AssignmentBuilder.new()
            .with_assignees(assignees=Logins.empty())
            .with_allow_no_assignees(allow_no_assignees=False)
            .build()
        )


def test_assign_when_a_draft_is_assigned_and_drafts_are_skipped_then_the_pull_request_stays_unchanged() -> None:
    # Given a draft pull request without assignees
    pull_request = PullRequest(number=7, draft=True, author=Login(value='carol'), assignees=Logins.empty())

    # When the pull request is assigned to alice while drafts are skipped
    assigned_pull_request = pull_request.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.from_raw(values=('alice',)))
        .with_eligibility(eligibility=Eligibility(skip_bots=False, skip_drafts=True))
        .build()
    )

    # Then the pull request stays without assignees
    assert assigned_pull_request == PullRequest(
        number=7,
        draft=True,
        author=Login(value='carol'),
        assignees=Logins.empty()
    )


def test_assign_when_a_draft_is_assigned_and_drafts_are_not_skipped_then_pull_request_carries_the_assignees() -> None:
    # Given a draft pull request without assignees
    pull_request = PullRequest(number=7, draft=True, author=Login(value='carol'), assignees=Logins.empty())

    # When the pull request is assigned to alice while drafts are not skipped
    assigned_pull_request = pull_request.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.from_raw(values=('alice',)))
        .with_eligibility(eligibility=Eligibility(skip_bots=False, skip_drafts=False))
        .build()
    )

    # Then the pull request carries alice
    assert assigned_pull_request.assignees == Logins.from_raw(values=('alice',))
