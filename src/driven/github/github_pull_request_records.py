from typing import final

from github.PullRequest import PullRequest
from github.Repository import Repository


@final
class GitHubPullRequestRecords:

    def __init__(self, repository: Repository, triggering_numbers: tuple[int, ...] | None) -> None:
        self._repository = repository
        self._triggering_numbers = triggering_numbers

    def in_scope(self) -> tuple[PullRequest, ...]:
        if self._triggering_numbers is None:
            return tuple(self._repository.get_pulls())

        return tuple(self._repository.get_pull(number=number) for number in self._triggering_numbers)
