from src.application.commands.assign_pull_requests_and_issues import AssignPullRequestsAndIssues
from src.driver.console.models.request import Request
from src.driver.console.pull_requests_and_issues_assigner import PullRequestsAndIssuesAssigner
from tests.support.spies.pull_requests_and_issues_assigning_spy import PullRequestsAndIssuesAssigningSpy


def test_assign_when_a_request_arrives_then_the_use_case_receives_its_command() -> None:
    # Given an assigner over the pull requests and issues use case
    pull_requests_and_issues = PullRequestsAndIssuesAssigningSpy()

    # When a request for pull requests and issues arrives
    PullRequestsAndIssuesAssigner(pull_requests_and_issues=pull_requests_and_issues).assign(
        request=Request(
            actor='octocat',
            assignees=('carol', 'dave'),
            skip_bots=True,
            skip_drafts=True,
            assign_author=False,
            allow_self_assign=False,
            allow_no_assignees=True,
            assignment_options=()
        )
    )

    # Then the use case receives the command carrying the request values
    assert pull_requests_and_issues.commands == [
        AssignPullRequestsAndIssues(
            actor='octocat',
            assignees=('carol', 'dave'),
            skip_bots=True,
            skip_drafts=True,
            assign_author=False,
            allow_self_assign=False,
            allow_no_assignees=True
        )
    ]
