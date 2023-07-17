from typing import List

from github.Repository import Repository

from src.application.domain.models.PullRequest import PullRequest
from src.application.ports.outbound.PullRequests import PullRequests


class Adapter(PullRequests):

    def __init__(self, repository: Repository) -> None:
        self.__repository = repository

    def all(self) -> List[PullRequest]:
        pulls = []
        records = self.__repository.get_pulls()

        if not records:
            return pulls

        for record in records:
            if not record.assignees:
                assignees = [assignee.login for assignee in record.assignees]
                pulls.append(PullRequest(number=record.number, assignees=assignees))

        return pulls

    def apply(self, assigned_pull: PullRequest):
        assignees = assigned_pull.assignees
        pull = self.__repository.get_pull(number=assigned_pull.number)
        pull.add_to_assignees(*assignees)
