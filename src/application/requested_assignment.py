from typing import final

from src.application.commands.assignment_command import AssignmentCommand
from src.application.domain.models.commons.assignment import Assignment
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.ports.outbound.assignees import Assignees


@final
class RequestedAssignment:

    def __init__(self, assignees: Assignees) -> None:
        self._assignees = assignees

    def from_command(self, command: AssignmentCommand) -> Assignment:
        return Assignment(
            actor=Login(value=command.actor),
            assignees=self._assignees.assignable(logins=Logins.from_raw(values=command.assignees)),
            eligibility=Eligibility(skip_bots=command.skip_bots, skip_drafts=command.skip_drafts),
            assign_author=command.assign_author,
            allow_self_assign=command.allow_self_assign,
            allow_no_assignees=command.allow_no_assignees
        )
