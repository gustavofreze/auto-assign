from typing import final

from github import GithubException
from github.Repository import Repository

from src.application.domain.models.commons.logins import Logins
from src.application.ports.outbound.assignees import Assignees
from src.driven.github.github_request_failed import GitHubRequestFailed


@final
class GitHubAssignees(Assignees):

    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def assignable(self, logins: Logins) -> Logins:
        try:
            members = Logins.from_raw(values=tuple(member.login for member in self._repository.get_assignees()))
        except GithubException as lookup_failure:
            raise GitHubRequestFailed(status=lookup_failure.status, operation='list assignees') from lookup_failure

        return logins.shared_with(other=members)
