from abc import ABC, abstractmethod

from src.application.commands.assign_issues import AssignIssues


class IssuesAssigning(ABC):
    """Assigning of the open issues that have no assignee yet."""

    @abstractmethod
    def handle(self, command: AssignIssues) -> None:
        """Assigns every open issue without an assignee to the assignees the repository accepts.

        :param command: The assignment requested by the actor.
        :raises AssigneesRequired: When no assignee remains and an empty assignment is not allowed.
        :raises SelfAssignmentNotAllowed: When the actor is among the assignees and self-assignment is denied.
        """
