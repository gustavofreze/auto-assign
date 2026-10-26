from dataclasses import dataclass
from typing import final

from src.application.domain.models.commons.assignment import Assignment
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Issue:
    number: int
    author: Login
    assignees: Logins

    def assign(self, assignment: Assignment) -> Issue:
        if assignment.excludes(author=self.author, draft=False):
            return self

        return Issue(number=self.number, author=self.author, assignees=assignment.granted_assignees(author=self.author))
