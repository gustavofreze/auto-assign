from typing import final

from src.application.commands.assign_issues import AssignIssues
from src.application.ports.inbound.issues_assigning import IssuesAssigning


@final
class IssuesAssigningSpy(IssuesAssigning):

    def __init__(self, failure: Exception | None) -> None:
        self.commands: list[AssignIssues] = []
        self._failure = failure

    def handle(self, command: AssignIssues) -> None:
        self.commands.append(command)

        if self._failure is not None:
            raise self._failure
