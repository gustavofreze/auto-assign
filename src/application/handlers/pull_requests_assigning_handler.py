from typing import final

from src.application.commands.assign_pull_requests import AssignPullRequests
from src.application.requested_assignment import RequestedAssignment
from src.application.ports.inbound.pull_requests_assigning import PullRequestsAssigning
from src.application.ports.outbound.assignees import Assignees
from src.application.ports.outbound.pull_requests import PullRequests


@final
class PullRequestsAssigningHandler(PullRequestsAssigning):

    def __init__(self, assignees: Assignees, pull_requests: PullRequests) -> None:
        self._requested_assignment = RequestedAssignment(assignees=assignees)
        self._pull_requests = pull_requests

    def handle(self, command: AssignPullRequests) -> None:
        unassigned = self._pull_requests.unassigned()

        if not unassigned:
            return

        assignment = self._requested_assignment.from_command(command=command)

        for pull_request in unassigned:
            self._pull_requests.assign(pull_request=pull_request.assign(assignment=assignment))
