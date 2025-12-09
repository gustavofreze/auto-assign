from typing import List
from unittest.mock import MagicMock

from test.mocks.issue.GitHubIssueMock import GitHubIssueMock
from test.mocks.issue.GitHubPullRequestMock import GitHubPullRequestMock
from test.mocks.issue.GitHubUserMock import GitHubUserMock

from github import GithubException
from github.Repository import Repository
from nacl.utils import random


class RepositoryMock(MagicMock):

    def __init__(self) -> None:
        super().__init__(spec=Repository)
        self.get_pull = None
        self.get_pulls = None
        self.get_issue = None
        self.get_issues = None
        self.get_assignees = None

    def add_issues(self, issues: List[dict]) -> None:
        issues = [GitHubIssueMock(number=issue.get('number'), assignees=issue.get('assignees')) for issue in issues]
        self.get_issues = MagicMock(return_value=issues)
        self.get_issue = MagicMock(return_value=issues[0])

    def add_assignees(self, assignees: List[str]) -> None:
        assignees = [GitHubUserMock(login=login) for login in assignees]
        self.get_assignees = MagicMock(return_value=assignees)

    def add_pull_requests(self, pulls: List[dict]) -> None:
        pulls = [GitHubPullRequestMock(number=pull.get('number'), assignees=pull.get('assignees')) for pull in pulls]
        self.get_pulls = MagicMock(return_value=pulls)
        self.get_pull = MagicMock(return_value=pulls[0])

    def remove_issues(self) -> None:
        self.get_issues = MagicMock(return_value=[])
        self.get_issue = MagicMock(return_value=None)

    def remove_assignees(self, assignees: List[str]) -> None:
        assignees = [GitHubUserMock(login=str(random(10))) for _ in assignees]
        self.get_assignees = MagicMock(return_value=assignees)

    def remove_pull_requests(self) -> None:
        self.get_pulls = MagicMock(return_value=[])
        self.get_pull = MagicMock(return_value=None)

    def with_assignees_exception(self, exception: GithubException):
        self.get_assignees = MagicMock(side_effect=exception)
