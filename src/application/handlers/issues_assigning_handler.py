from typing import final

from src.application.commands.assign_issues import AssignIssues
from src.application.requested_assignment import RequestedAssignment
from src.application.ports.inbound.issues_assigning import IssuesAssigning
from src.application.ports.outbound.assignees import Assignees
from src.application.ports.outbound.issues import Issues


@final
class IssuesAssigningHandler(IssuesAssigning):

    def __init__(self, issues: Issues, assignees: Assignees) -> None:
        self._issues = issues
        self._requested_assignment = RequestedAssignment(assignees=assignees)

    def handle(self, command: AssignIssues) -> None:
        unassigned = self._issues.unassigned()

        if not unassigned:
            return

        assignment = self._requested_assignment.from_command(command=command)

        for issue in unassigned:
            self._issues.assign(issue=issue.assign(assignment=assignment))
