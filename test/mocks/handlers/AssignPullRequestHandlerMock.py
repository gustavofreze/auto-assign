from unittest.mock import MagicMock

from src.application.commands.AssignPullRequests import AssignPullRequests
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler


class AssignPullRequestHandlerMock(MagicMock):

    def __init__(self) -> None:
        super().__init__(spec=AssignPullRequestHandler)
        self.handle = MagicMock(side_effect=self._capture_command)
        self.handled_commands = []

    def _capture_command(self, command: AssignPullRequests):
        self.handled_commands.append(command)

    def with_exception(self, exception: Exception):
        self.handle.side_effect = exception

    def reset(self):
        super().reset_mock()
        self.handled_commands = []
        self.handle.side_effect = self._capture_command
