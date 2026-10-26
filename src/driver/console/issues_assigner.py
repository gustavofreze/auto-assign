from typing import final

from src.application.commands.assign_issues import AssignIssues
from src.application.ports.inbound.issues_assigning import IssuesAssigning
from src.driver.console.assigner import Assigner
from src.driver.console.models.request import Request


@final
class IssuesAssigner(Assigner):

    def __init__(self, issues: IssuesAssigning) -> None:
        self._issues = issues

    def assign(self, request: Request) -> None:
        command = AssignIssues(
            actor=request.actor,
            assignees=request.assignees,
            skip_bots=request.skip_bots,
            skip_drafts=request.skip_drafts,
            assign_author=request.assign_author,
            allow_self_assign=request.allow_self_assign,
            allow_no_assignees=request.allow_no_assignees
        )
        self._issues.handle(command=command)
