from abc import ABC, abstractmethod

from src.application.domain.models.issue import Issue


class Issues(ABC):
    """Open issues of the repository."""

    @abstractmethod
    def unassigned(self) -> tuple[Issue, ...]:
        """Lists the open issues that have no assignee.

        :returns: The open issues without an assignee.
        """

    @abstractmethod
    def assign(self, issue: Issue) -> None:
        """Records the assignees of the issue in the repository.

        :param issue: The issue carrying its granted assignees.
        """
