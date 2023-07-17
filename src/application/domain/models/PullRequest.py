from dataclasses import dataclass
from typing import List

from src.application.domain.events.AssignedPullRequest import AssignedPullRequest
from src.application.domain.exceptions.MissingAssignees import MissingAssignees
from src.application.domain.exceptions.PullRequestNotAssigned import PullRequestNotAssigned


@dataclass
class PullRequest:

    def __init__(self, number: int, assignees: List[str]) -> None:
        self.number = number
        self.assignees = assignees

    def assign(
            self,
            actor: str,
            assignees: List[str],
            allow_self_assign: bool,
            allow_no_assignees: bool
    ) -> AssignedPullRequest:
        if not assignees and not allow_no_assignees:
            raise MissingAssignees()

        if actor in assignees and not allow_self_assign and not allow_no_assignees:
            raise PullRequestNotAssigned(assignee=actor)

        return AssignedPullRequest(number=self.number, assignees=assignees)
