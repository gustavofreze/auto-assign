from dataclasses import dataclass
from typing import List


@dataclass
class AssignedIssue:

    def __init__(self, number: int, assignees: List[str]) -> None:
        self.number = number
        self.assignees = assignees
