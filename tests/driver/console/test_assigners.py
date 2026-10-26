import logging

import pytest

from src.application.domain.exceptions.assignees_required import AssigneesRequired
from src.driver.console.assigners import Assigners
from src.driver.console.issues_assigner import IssuesAssigner
from src.driver.console.models.assignment_kind import AssignmentKind
from src.driver.console.models.code import Code
from src.driver.console.models.request import Request
from src.driver.console.models.result import Result
from src.driver.console.pull_requests_and_issues_assigner import PullRequestsAndIssuesAssigner
from src.driver.console.pull_requests_assigner import PullRequestsAssigner
from tests.support.spies.issues_assigning_spy import IssuesAssigningSpy
from tests.support.spies.pull_requests_and_issues_assigning_spy import PullRequestsAndIssuesAssigningSpy
from tests.support.spies.pull_requests_assigning_spy import PullRequestsAssigningSpy


def request_for(assignment_options: tuple[str, ...]) -> Request:
    return Request(
        actor='octocat',
        assignees=('alice',),
        skip_bots=False,
        skip_drafts=False,
        assign_author=False,
        allow_self_assign=True,
        allow_no_assignees=False,
        assignment_options=assignment_options
    )


def assigners_over(
        issues: IssuesAssigningSpy,
        pull_requests: PullRequestsAssigningSpy,
        pull_requests_and_issues: PullRequestsAndIssuesAssigningSpy
) -> Assigners:
    return Assigners(
        logger=logging.getLogger('test'),
        assigners={
            AssignmentKind.ISSUES: IssuesAssigner(issues=issues),
            AssignmentKind.PULL_REQUESTS: PullRequestsAssigner(pull_requests=pull_requests),
            AssignmentKind.PULL_REQUESTS_AND_ISSUES: PullRequestsAndIssuesAssigner(
                pull_requests_and_issues=pull_requests_and_issues
            )
        }
    )


def test_assign_when_issues_are_requested_then_only_issues_are_assigned_and_the_result_succeeds() -> None:
    # Given an assigner over the three use cases
    issues = IssuesAssigningSpy(failure=None)
    pull_requests = PullRequestsAssigningSpy()
    pull_requests_and_issues = PullRequestsAndIssuesAssigningSpy()
    assigners = assigners_over(
        issues=issues,
        pull_requests=pull_requests,
        pull_requests_and_issues=pull_requests_and_issues
    )

    # When issues are requested
    result = assigners.assign(request=request_for(assignment_options=('ISSUE',)))

    # Then the result succeeds
    assert result == Result.success()

    # And only the issues use case was called
    assert (len(issues.commands), len(pull_requests.commands), len(pull_requests_and_issues.commands)) == (1, 0, 0)


def test_assign_when_pull_requests_are_requested_then_only_pull_requests_are_assigned() -> None:
    # Given an assigner over the three use cases
    issues = IssuesAssigningSpy(failure=None)
    pull_requests = PullRequestsAssigningSpy()
    pull_requests_and_issues = PullRequestsAndIssuesAssigningSpy()
    assigners = assigners_over(
        issues=issues,
        pull_requests=pull_requests,
        pull_requests_and_issues=pull_requests_and_issues
    )

    # When pull requests are requested
    assigners.assign(request=request_for(assignment_options=('PULL_REQUEST',)))

    # Then only the pull requests use case was called
    assert (len(issues.commands), len(pull_requests.commands), len(pull_requests_and_issues.commands)) == (0, 1, 0)


@pytest.mark.parametrize(
    ids=['issue first', 'pull request first'],
    argnames=['assignment_options'],
    argvalues=[(('ISSUE', 'PULL_REQUEST'),), (('PULL_REQUEST', 'ISSUE'),)]
)
def test_assign_when_both_are_requested_in_any_order_then_only_the_combined_use_case_is_called(
        assignment_options: tuple[str, ...]
) -> None:
    # Given an assigner over the three use cases
    issues = IssuesAssigningSpy(failure=None)
    pull_requests = PullRequestsAssigningSpy()
    pull_requests_and_issues = PullRequestsAndIssuesAssigningSpy()
    assigners = assigners_over(
        issues=issues,
        pull_requests=pull_requests,
        pull_requests_and_issues=pull_requests_and_issues
    )

    # When pull requests and issues are requested
    assigners.assign(request=request_for(assignment_options=assignment_options))

    # Then only the combined use case was called
    assert (len(issues.commands), len(pull_requests.commands), len(pull_requests_and_issues.commands)) == (0, 0, 1)


@pytest.mark.parametrize(
    ids=['no option', 'unknown option', 'option with a known one'],
    argnames=['assignment_options'],
    argvalues=[((),), (('DISCUSSION',),), (('ISSUE', 'DISCUSSION'),)]
)
def test_assign_when_options_are_invalid_then_the_result_reports_missing_configuration(
        assignment_options: tuple[str, ...]
) -> None:
    # Given an assigner over the three use cases
    assigners = assigners_over(
        issues=IssuesAssigningSpy(failure=None),
        pull_requests=PullRequestsAssigningSpy(),
        pull_requests_and_issues=PullRequestsAndIssuesAssigningSpy()
    )

    # When the request carries invalid assignment options
    result = assigners.assign(request=request_for(assignment_options=assignment_options))

    # Then the result reports missing configuration
    assert result.code == Code.CONFIGURATION_MISSING


@pytest.mark.parametrize(
    ids=['domain rule violated', 'unexpected failure', 'unexpected failure without a message'],
    argnames=['failure', 'expected'],
    argvalues=[
        (AssigneesRequired(), Result.assignment_failure(message='Assignees are required.')),
        (RuntimeError('boom'), Result.unexpected_failure(message='boom')),
        (RuntimeError(), Result.unexpected_failure(message='An unexpected error occurred.'))
    ]
)
def test_assign_when_the_use_case_fails_then_the_result_maps_the_failure_to_its_code_and_message(
        expected: Result,
        failure: Exception
) -> None:
    # Given an issues use case that fails
    assigners = assigners_over(
        issues=IssuesAssigningSpy(failure=failure),
        pull_requests=PullRequestsAssigningSpy(),
        pull_requests_and_issues=PullRequestsAndIssuesAssigningSpy()
    )

    # When issues are requested
    result = assigners.assign(request=request_for(assignment_options=('ISSUE',)))

    # Then the result carries the code and the message of that failure
    assert result == expected


@pytest.mark.parametrize(
    ids=['invalid options', 'domain rule violated', 'unexpected failure'],
    argnames=['assignment_options', 'failure', 'traceback_logged'],
    argvalues=[
        (('DISCUSSION',), None, False),
        (('ISSUE',), AssigneesRequired(), False),
        (('ISSUE',), RuntimeError('boom'), True)
    ]
)
def test_assign_when_the_assignment_fails_then_only_an_unexpected_failure_logs_its_traceback(
        caplog: pytest.LogCaptureFixture,
        failure: Exception | None,
        traceback_logged: bool,
        assignment_options: tuple[str, ...]
) -> None:
    # Given an issues use case that may fail
    assigners = assigners_over(
        issues=IssuesAssigningSpy(failure=failure),
        pull_requests=PullRequestsAssigningSpy(),
        pull_requests_and_issues=PullRequestsAndIssuesAssigningSpy()
    )

    # When the request is assigned
    assigners.assign(request=request_for(assignment_options=assignment_options))

    # Then one error is logged, with a traceback only for an unexpected failure
    assert [(record.levelno, bool(record.exc_info)) for record in caplog.records] == [
        (logging.ERROR, traceback_logged)
    ]
