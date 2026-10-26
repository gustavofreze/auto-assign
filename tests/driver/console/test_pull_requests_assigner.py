from src.application.commands.assign_pull_requests import AssignPullRequests
from src.driver.console.models.request import Request
from src.driver.console.pull_requests_assigner import PullRequestsAssigner
from tests.support.spies.pull_requests_assigning_spy import PullRequestsAssigningSpy


def test_assign_when_a_request_arrives_then_the_use_case_receives_its_command() -> None:
    # Given an assigner over the pull requests use case
    pull_requests = PullRequestsAssigningSpy()

    # When a request for pull requests arrives
    PullRequestsAssigner(pull_requests=pull_requests).assign(
        request=Request(
            actor='octocat',
            assignees=('bob', 'carol'),
            skip_bots=False,
            skip_drafts=True,
            assign_author=True,
            allow_self_assign=False,
            allow_no_assignees=True,
            assignment_options=()
        )
    )

    # Then the use case receives the command carrying the request values
    assert pull_requests.commands == [
        AssignPullRequests(
            actor='octocat',
            assignees=('bob', 'carol'),
            skip_bots=False,
            skip_drafts=True,
            assign_author=True,
            allow_self_assign=False,
            allow_no_assignees=True
        )
    ]
