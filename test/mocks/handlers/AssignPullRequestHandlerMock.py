from unittest.mock import MagicMock

from src.application.commands.AssignPullRequests import AssignPullRequests
from src.application.domain.exceptions.PullRequestNotAssigned import PullRequestNotAssigned
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler


class AssignPullRequestHandlerMock(MagicMock):

    def __init__(self) -> None:
        super().__init__(spec=AssignPullRequestHandler)
        self._pull_request_not_assigned = False

    def handle(self, command: AssignPullRequests):
        if self._pull_request_not_assigned is None:
            return

        raise PullRequestNotAssigned(assignee=command.actor)

    def with_pull_request_not_assigned(self):
        self._pull_request_not_assigned = True
        return self
