from abc import ABC, abstractmethod
from typing import List

from src.application.domain.events.AssignedIssue import AssignedIssue
from src.application.domain.models.Issue import Issue


class Issues(ABC):

    @abstractmethod
    def all(self) -> List[Issue]:
        """
        Find all available issues.

        :returns: A list of :class:`Issue`.
        """

    @abstractmethod
    def apply(self, assigned_issue: AssignedIssue):
        """
        Applies assignee assignment to an :class:`Issue`.

        :param assigned_issue: Issue assigned with one or more assignees.
        :type assigned_issue: AssignedIssue
        """
