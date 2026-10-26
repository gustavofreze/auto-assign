from typing import final

from src.application.domain.models.commons.logins import Logins
from src.application.ports.outbound.assignees import Assignees


@final
class AssigneesSpy(Assignees):

    def __init__(self, assignable_logins: Logins) -> None:
        self.requested_logins: list[Logins] = []
        self._assignable_logins = assignable_logins

    def assignable(self, logins: Logins) -> Logins:
        self.requested_logins.append(logins)
        return self._assignable_logins
