from typing import final

from src.application.commands.assign_pull_requests import AssignPullRequests
from src.application.ports.inbound.pull_requests_assigning import PullRequestsAssigning


@final
class PullRequestsAssigningSpy(PullRequestsAssigning):

    def __init__(self) -> None:
        self.commands: list[AssignPullRequests] = []

    def handle(self, command: AssignPullRequests) -> None:
        self.commands.append(command)
