from dataclasses import dataclass
from typing import List

from src.application.domain.events.AssignedIssue import AssignedIssue
from src.application.domain.exceptions.IssueNotAssigned import IssueNotAssigned
from src.application.domain.exceptions.MissingAssignees import MissingAssignees


@dataclass
class Issue:

    def __init__(self, number: int, assignees: List[str]) -> None:
        self.number = number
        self.assignees = assignees

    def assign(
            self,
            actor: str,
            assignees: List[str],
            allow_self_assign: bool,
            allow_no_assignees: bool
    ) -> AssignedIssue:
        if not assignees and not allow_no_assignees:
            raise MissingAssignees()

        if actor in assignees and not allow_self_assign and not allow_no_assignees:
            raise IssueNotAssigned(assignee=actor)

        return AssignedIssue(number=self.number, assignees=assignees)
