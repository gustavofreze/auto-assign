from typing import List
from unittest.mock import MagicMock

from github.Issue import Issue


class GitHubIssueMock(MagicMock):

    def __init__(self, number: int, assignees: List[str]) -> None:
        super().__init__(spec=Issue)
        self.number = number
        self.assignees = assignees
        self.pull_request = False
        self.add_to_assignees = MagicMock()
