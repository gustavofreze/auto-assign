from unittest.mock import MagicMock

from src.application.commands.AssignIssues import AssignIssues
from src.application.domain.exceptions.IssueNotAssigned import IssueNotAssigned
from src.application.handlers.AssignIssueHandler import AssignIssueHandler


class AssignIssueHandlerMock(MagicMock):

    def __init__(self) -> None:
        super().__init__(spec=AssignIssueHandler)
        self.issue_not_assigned = False

    def handle(self, command: AssignIssues):
        if self.issue_not_assigned is None:
            return

        raise IssueNotAssigned(assignee=command.actor)

    def with_issue_not_assigned(self):
        self.issue_not_assigned = True
        return self

    def reset_mock(self, *args, **kwargs) -> None:
        super().reset_mock(*args, **kwargs)
        self.issue_not_assigned = False
