from abc import ABC, abstractmethod

from src.application.commands.assign_pull_requests_and_issues import AssignPullRequestsAndIssues


class PullRequestsAndIssuesAssigning(ABC):
    """Assigning of the open pull requests and issues that have no assignee yet."""

    @abstractmethod
    def handle(self, command: AssignPullRequestsAndIssues) -> None:
        """Assigns every open pull request and issue without an assignee to the assignees the repository accepts.

        :param command: The assignment requested by the actor.
        :raises AssigneesRequired: When no assignee remains and an empty assignment is not allowed.
        :raises SelfAssignmentNotAllowed: When the actor is among the assignees and self-assignment is denied.
        """
