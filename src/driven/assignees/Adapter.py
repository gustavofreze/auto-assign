from typing import List

from github import GithubException
from github.Repository import Repository

from src.application.ports.outbound.Assignees import Assignees


class Adapter(Assignees):

    def __init__(self, repository: Repository) -> None:
        self.__repository = repository

    def exists(self, assignees: List[str]) -> List[str]:
        try:
            contributors = [contributor.login for contributor in self.__repository.get_contributors()]
            valid_assignees = [assignee for assignee in assignees if assignee in contributors]

            return valid_assignees

        except GithubException:
            return []
