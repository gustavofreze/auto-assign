from typing import final

from src.application.commands.assign_pull_requests import AssignPullRequests
from src.application.ports.inbound.pull_requests_assigning import PullRequestsAssigning
from src.driver.console.assigner import Assigner
from src.driver.console.models.request import Request


@final
class PullRequestsAssigner(Assigner):

    def __init__(self, pull_requests: PullRequestsAssigning) -> None:
        self._pull_requests = pull_requests

    def assign(self, request: Request) -> None:
        command = AssignPullRequests(
            actor=request.actor,
            assignees=request.assignees,
            skip_bots=request.skip_bots,
            skip_drafts=request.skip_drafts,
            assign_author=request.assign_author,
            allow_self_assign=request.allow_self_assign,
            allow_no_assignees=request.allow_no_assignees
        )
        self._pull_requests.handle(command=command)
