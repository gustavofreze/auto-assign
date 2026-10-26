from dataclasses import dataclass
from typing import final

from src.application.domain.exceptions.assignees_required import AssigneesRequired
from src.application.domain.exceptions.self_assignment_not_allowed import SelfAssignmentNotAllowed
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Assignment:
    actor: Login
    assignees: Logins
    eligibility: Eligibility
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool

    def excludes(self, author: Login, draft: bool) -> bool:
        return self.eligibility.excludes(author=author, draft=draft)

    def granted_assignees(self, author: Login) -> Logins:
        authors = Logins(elements=(author,)) if self.assign_author else Logins.empty()

        if not self.assignees and not authors and not self.allow_no_assignees:
            raise AssigneesRequired()

        if self.actor not in self.assignees or self.allow_self_assign:
            return self.assignees.including(other=authors)

        if not self.allow_no_assignees:
            raise SelfAssignmentNotAllowed(actor=self.actor)

        return self.assignees.without(login=self.actor).including(other=authors)
