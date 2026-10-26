from dataclasses import dataclass
from typing import final

from src.application.domain.models.commons.assignment import Assignment
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AssignmentBuilder:
    actor: Login
    assignees: Logins
    eligibility: Eligibility
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool

    @staticmethod
    def new() -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=Login(value='octocat'),
            assignees=Logins.from_raw(values=('alice', 'bob')),
            eligibility=Eligibility(skip_bots=False, skip_drafts=False),
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        )

    def with_actor(self, actor: Login) -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=actor,
            assignees=self.assignees,
            eligibility=self.eligibility,
            assign_author=self.assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )

    def with_assignees(self, assignees: Logins) -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=self.actor,
            assignees=assignees,
            eligibility=self.eligibility,
            assign_author=self.assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )

    def with_eligibility(self, eligibility: Eligibility) -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=self.actor,
            assignees=self.assignees,
            eligibility=eligibility,
            assign_author=self.assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )

    def with_assign_author(self, assign_author: bool) -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=self.actor,
            assignees=self.assignees,
            eligibility=self.eligibility,
            assign_author=assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )

    def with_allow_self_assign(self, allow_self_assign: bool) -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=self.actor,
            assignees=self.assignees,
            eligibility=self.eligibility,
            assign_author=self.assign_author,
            allow_self_assign=allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )

    def with_allow_no_assignees(self, allow_no_assignees: bool) -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=self.actor,
            assignees=self.assignees,
            eligibility=self.eligibility,
            assign_author=self.assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=allow_no_assignees
        )

    def build(self) -> Assignment:
        return Assignment(
            actor=self.actor,
            assignees=self.assignees,
            eligibility=self.eligibility,
            assign_author=self.assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )
