from typing import final

from src.application.commands.assign_pull_requests_and_issues import AssignPullRequestsAndIssues
from src.application.requested_assignment import RequestedAssignment
from src.application.ports.inbound.pull_requests_and_issues_assigning import PullRequestsAndIssuesAssigning
from src.application.ports.outbound.assignees import Assignees
from src.application.ports.outbound.issues import Issues
from src.application.ports.outbound.pull_requests import PullRequests


@final
class PullRequestsAndIssuesAssigningHandler(PullRequestsAndIssuesAssigning):

    def __init__(self, issues: Issues, assignees: Assignees, pull_requests: PullRequests) -> None:
        self._issues = issues
        self._requested_assignment = RequestedAssignment(assignees=assignees)
        self._pull_requests = pull_requests

    def handle(self, command: AssignPullRequestsAndIssues) -> None:
        unassigned_pull_requests = self._pull_requests.unassigned()
        unassigned_issues = self._issues.unassigned()

        if not unassigned_pull_requests and not unassigned_issues:
            return

        assignment = self._requested_assignment.from_command(command=command)

        for pull_request in unassigned_pull_requests:
            self._pull_requests.assign(pull_request=pull_request.assign(assignment=assignment))

        for issue in unassigned_issues:
            self._issues.assign(issue=issue.assign(assignment=assignment))
