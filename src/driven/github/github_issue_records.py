from typing import final

from github.Issue import Issue
from github.Repository import Repository

UNASSIGNED = 'none'


@final
class GitHubIssueRecords:

    def __init__(self, repository: Repository, triggering_numbers: tuple[int, ...] | None) -> None:
        self._repository = repository
        self._triggering_numbers = triggering_numbers

    def in_scope(self) -> tuple[Issue, ...]:
        if self._triggering_numbers is None:
            return tuple(self._repository.get_issues(assignee=UNASSIGNED))

        return tuple(self._repository.get_issue(number=number) for number in self._triggering_numbers)
