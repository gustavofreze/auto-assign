from typing import final

from github import GithubException
from github.Repository import Repository

from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.issue import Issue
from src.application.ports.outbound.issues import Issues
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_issue_records import GitHubIssueRecords
from src.driven.github.github_request_failed import GitHubRequestFailed
from src.driven.github.item_kind import ItemKind
from src.driven.github.journal_entry import JournalEntry

OPEN_STATE = 'open'


@final
class GitHubIssues(Issues):

    def __init__(self, records: GitHubIssueRecords, journal: AssignmentJournal, repository: Repository) -> None:
        self._records = records
        self._journal = journal
        self._repository = repository

    def unassigned(self) -> tuple[Issue, ...]:
        try:
            return tuple(
                Issue(number=record.number, author=Login(value=record.user.login), assignees=Logins.empty())
                for record in self._records.in_scope()
                if record.state == OPEN_STATE and not record.assignees and record.pull_request is None
            )
        except GithubException as listing_failure:
            raise GitHubRequestFailed(status=listing_failure.status, operation='list issues') from listing_failure

    def assign(self, issue: Issue) -> None:
        if not issue.assignees:
            return

        try:
            record = self._repository.get_issue(number=issue.number)
            record.add_to_assignees(*(assignee.value for assignee in issue.assignees))
        except GithubException as assignment_failure:
            raise GitHubRequestFailed(
                status=assignment_failure.status,
                operation='assign an issue'
            ) from assignment_failure

        self._journal.record(
            entry=JournalEntry(
                kind=ItemKind.ISSUE,
                number=issue.number,
                assignees=tuple(assignee.login for assignee in record.assignees)
            )
        )
