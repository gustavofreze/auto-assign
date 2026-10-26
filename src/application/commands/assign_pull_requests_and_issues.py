from dataclasses import dataclass
from typing import final

from src.application.commands.assignment_command import AssignmentCommand


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AssignPullRequestsAndIssues(AssignmentCommand):
    pass
