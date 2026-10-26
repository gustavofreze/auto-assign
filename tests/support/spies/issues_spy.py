from typing import final

from src.application.domain.models.issue import Issue
from src.application.ports.outbound.issues import Issues


@final
class IssuesSpy(Issues):

    def __init__(self, unassigned_issues: tuple[Issue, ...]) -> None:
        self.assigned_issues: list[Issue] = []
        self._unassigned_issues = unassigned_issues

    def unassigned(self) -> tuple[Issue, ...]:
        return self._unassigned_issues

    def assign(self, issue: Issue) -> None:
        self.assigned_issues.append(issue)
