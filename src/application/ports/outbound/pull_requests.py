from abc import ABC, abstractmethod

from src.application.domain.models.pull_request import PullRequest


class PullRequests(ABC):
    """Open pull requests of the repository."""

    @abstractmethod
    def unassigned(self) -> tuple[PullRequest, ...]:
        """Lists the open pull requests that have no assignee.

        :returns: The open pull requests without an assignee.
        """

    @abstractmethod
    def assign(self, pull_request: PullRequest) -> None:
        """Records the assignees of the pull request in the repository.

        :param pull_request: The pull request carrying its granted assignees.
        """
