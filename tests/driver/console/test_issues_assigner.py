from src.application.commands.assign_issues import AssignIssues
from src.driver.console.issues_assigner import IssuesAssigner
from src.driver.console.models.request import Request
from tests.support.spies.issues_assigning_spy import IssuesAssigningSpy


def test_assign_when_a_request_arrives_then_the_use_case_receives_its_command() -> None:
    # Given an assigner over the issues use case
    issues = IssuesAssigningSpy(failure=None)

    # When a request for issues arrives
    IssuesAssigner(issues=issues).assign(
        request=Request(
            actor='octocat',
            assignees=('alice', 'bob'),
            skip_bots=True,
            skip_drafts=False,
            assign_author=True,
            allow_self_assign=False,
            allow_no_assignees=True,
            assignment_options=()
        )
    )

    # Then the use case receives the command carrying the request values
    assert issues.commands == [
        AssignIssues(
            actor='octocat',
            assignees=('alice', 'bob'),
            skip_bots=True,
            skip_drafts=False,
            assign_author=True,
            allow_self_assign=False,
            allow_no_assignees=True
        )
    ]
