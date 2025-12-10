from unittest.mock import MagicMock

from src.application.commands.AssignIssues import AssignIssues
from src.application.handlers.AssignIssueHandler import AssignIssueHandler


class AssignIssueHandlerMock(MagicMock):

    def __init__(self) -> None:
        super().__init__(spec=AssignIssueHandler)
        self.handle = MagicMock(side_effect=self._capture_command)
        self.handled_commands = []

    def _capture_command(self, command: AssignIssues):
        self.handled_commands.append(command)

    def with_exception(self, exception: Exception):
        self.handle.side_effect = exception

    def reset(self):
        super().reset_mock()
        self.handled_commands = []
        self.handle.side_effect = self._capture_command
