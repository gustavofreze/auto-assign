from typing import final

from src.application.domain.models.pull_request import PullRequest
from src.application.ports.outbound.pull_requests import PullRequests


@final
class PullRequestsSpy(PullRequests):

    def __init__(self, unassigned_pull_requests: tuple[PullRequest, ...]) -> None:
        self.assigned_pull_requests: list[PullRequest] = []
        self._unassigned_pull_requests = unassigned_pull_requests

    def unassigned(self) -> tuple[PullRequest, ...]:
        return self._unassigned_pull_requests

    def assign(self, pull_request: PullRequest) -> None:
        self.assigned_pull_requests.append(pull_request)
