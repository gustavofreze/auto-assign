from typing import List
from unittest.mock import MagicMock

from github.PullRequest import PullRequest


class GitHubPullRequestMock(MagicMock):

    def __init__(self, number: int, assignees: List[str]) -> None:
        super().__init__(spec=PullRequest)
        self.number = number
        self.assignees = assignees
        self.pull_request = True
        self.add_to_assignees = MagicMock()
