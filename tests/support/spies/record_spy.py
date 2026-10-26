from typing import final

from tests.support.spies.user_spy import UserSpy


@final
class RecordSpy:

    def __init__(
            self,
            user: UserSpy,
            draft: bool,
            state: str,
            number: int,
            assignees: tuple[UserSpy, ...],
            pull_request: object | None
    ) -> None:
        self.user = user
        self.draft = draft
        self.state = state
        self.number = number
        self.assignees = assignees
        self.pull_request = pull_request
        self.added_assignees: list[str] = []

    def add_to_assignees(self, *logins: str) -> None:
        self.added_assignees.extend(logins)
        self.assignees = (*self.assignees, *(UserSpy(login=login) for login in logins))
