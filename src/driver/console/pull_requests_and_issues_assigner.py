from typing import final

from src.application.commands.assign_pull_requests_and_issues import AssignPullRequestsAndIssues
from src.application.ports.inbound.pull_requests_and_issues_assigning import PullRequestsAndIssuesAssigning
from src.driver.console.assigner import Assigner
from src.driver.console.models.request import Request


@final
class PullRequestsAndIssuesAssigner(Assigner):

    def __init__(self, pull_requests_and_issues: PullRequestsAndIssuesAssigning) -> None:
        self._pull_requests_and_issues = pull_requests_and_issues

    def assign(self, request: Request) -> None:
        command = AssignPullRequestsAndIssues(
            actor=request.actor,
            assignees=request.assignees,
            skip_bots=request.skip_bots,
            skip_drafts=request.skip_drafts,
            assign_author=request.assign_author,
            allow_self_assign=request.allow_self_assign,
            allow_no_assignees=request.allow_no_assignees
        )
        self._pull_requests_and_issues.handle(command=command)
