from typing import final

from github import GithubException

from tests.support.spies.record_spy import RecordSpy
from tests.support.spies.user_spy import UserSpy


@final
class RepositorySpy:

    def __init__(
            self,
            records: tuple[RecordSpy, ...],
            members: tuple[str, ...],
            failure: GithubException | None
    ) -> None:
        self._records = records
        self._members = members
        self._failure = failure
        self.requested = False
        self.listed_assignee: str | None = None

    def get_assignees(self) -> tuple[UserSpy, ...]:
        self._receive_request()
        return tuple(UserSpy(login=member) for member in self._members)

    def get_issues(self, assignee: str) -> tuple[RecordSpy, ...]:
        self._receive_request()
        self.listed_assignee = assignee
        return self._records

    def get_pulls(self) -> tuple[RecordSpy, ...]:
        self._receive_request()
        return self._records

    def get_issue(self, number: int) -> RecordSpy:
        self._receive_request()
        return next(record for record in self._records if record.number == number)

    def get_pull(self, number: int) -> RecordSpy:
        return self.get_issue(number=number)

    def _receive_request(self) -> None:
        self.requested = True

        if self._failure is not None:
            raise self._failure
