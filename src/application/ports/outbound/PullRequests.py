from abc import ABC, abstractmethod
from typing import List

from src.application.domain.events.AssignedPullRequest import AssignedPullRequest
from src.application.domain.models.PullRequest import PullRequest


class PullRequests(ABC):

    @abstractmethod
    def all(self) -> List[PullRequest]:
        """
        Find all available pull requests.

        :returns: A list of :class:`PullRequest`.
        """

    @abstractmethod
    def apply(self, assigned_pull: AssignedPullRequest):
        """
        Applies assignee assignment to an :class:`PullRequest`.

        :param assigned_pull: Pull request assigned with one or more assignees.
        :type assigned_pull: AssignedPullRequest
        """
