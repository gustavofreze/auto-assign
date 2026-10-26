from typing import final

from src.application.commands.assign_pull_requests_and_issues import AssignPullRequestsAndIssues
from src.application.ports.inbound.pull_requests_and_issues_assigning import PullRequestsAndIssuesAssigning


@final
class PullRequestsAndIssuesAssigningSpy(PullRequestsAndIssuesAssigning):

    def __init__(self) -> None:
        self.commands: list[AssignPullRequestsAndIssues] = []

    def handle(self, command: AssignPullRequestsAndIssues) -> None:
        self.commands.append(command)
