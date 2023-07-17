from typing import List

from github.Repository import Repository

from src.application.domain.events.AssignedIssue import AssignedIssue
from src.application.domain.models.Issue import Issue
from src.application.ports.outbound.Issues import Issues


class Adapter(Issues):

    def __init__(self, repository: Repository) -> None:
        self.__repository = repository

    def all(self) -> List[Issue]:
        issues = []
        records = self.__repository.get_issues()

        if not records:
            return issues

        for record in records:
            if not record.assignees and not record.pull_request:
                assignees = [assignee.login for assignee in record.assignees]
                issues.append(Issue(number=record.number, assignees=assignees))

        return issues

    def apply(self, assigned_issue: AssignedIssue):
        assignees = assigned_issue.assignees
        issue = self.__repository.get_issue(number=assigned_issue.number)
        issue.add_to_assignees(*assignees)
