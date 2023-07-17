from dataclasses import dataclass
from typing import List


@dataclass
class AssignedPullRequest:

    def __init__(self, number: int, assignees: List[str]) -> None:
        self.number = number
        self.assignees = assignees
