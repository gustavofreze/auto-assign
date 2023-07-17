from dataclasses import dataclass
from typing import List

from src.application.commands.Command import Command


@dataclass
class AssignPullRequests(Command):

    def __init__(self, actor: str, assignees: List[str], allow_self_assign: bool, allow_no_assignees: bool) -> None:
        self.actor = actor
        self.assignees = assignees
        self.allow_self_assign = allow_self_assign
        self.allow_no_assignees = allow_no_assignees
