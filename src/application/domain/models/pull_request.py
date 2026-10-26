from dataclasses import dataclass
from typing import final

from src.application.domain.models.commons.assignment import Assignment
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PullRequest:
    number: int
    draft: bool
    author: Login
    assignees: Logins

    def assign(self, assignment: Assignment) -> PullRequest:
        if assignment.excludes(author=self.author, draft=self.draft):
            return self

        return PullRequest(
            number=self.number,
            draft=self.draft,
            author=self.author,
            assignees=assignment.granted_assignees(author=self.author)
        )
