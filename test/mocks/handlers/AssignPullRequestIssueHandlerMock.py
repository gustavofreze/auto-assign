from unittest.mock import MagicMock

from src.application.commands.AssignPullRequestIssue import AssignPullRequestIssue
from src.application.handlers.AssignPullRequestIssueHandler import AssignPullRequestIssueHandler


class AssignPullRequestIssueHandlerMock(MagicMock):

    def __init__(self) -> None:
        super().__init__(spec=AssignPullRequestIssueHandler)
        self.handle = MagicMock(side_effect=self._capture_command)
        self.handled_commands = []

    def _capture_command(self, command: AssignPullRequestIssue):
        self.handled_commands.append(command)

    def with_exception(self, exception: Exception):
        self.handle.side_effect = exception

    def reset(self):
        super().reset_mock()
        self.handled_commands = []
        self.handle.side_effect = self._capture_command
