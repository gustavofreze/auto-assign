from typing import final

from github import GithubException
from github.Repository import Repository

from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins
from src.application.domain.models.pull_request import PullRequest
from src.application.ports.outbound.pull_requests import PullRequests
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_pull_request_records import GitHubPullRequestRecords
from src.driven.github.github_request_failed import GitHubRequestFailed
from src.driven.github.item_kind import ItemKind
from src.driven.github.journal_entry import JournalEntry

OPEN_STATE = 'open'


@final
class GitHubPullRequests(PullRequests):

    def __init__(
            self,
            records: GitHubPullRequestRecords,
            journal: AssignmentJournal,
            repository: Repository
    ) -> None:
        self._records = records
        self._journal = journal
        self._repository = repository

    def unassigned(self) -> tuple[PullRequest, ...]:
        try:
            return tuple(
                PullRequest(
                    number=record.number,
                    draft=record.draft,
                    author=Login(value=record.user.login),
                    assignees=Logins.empty()
                )
                for record in self._records.in_scope()
                if record.state == OPEN_STATE and not record.assignees
            )
        except GithubException as listing_failure:
            raise GitHubRequestFailed(
                status=listing_failure.status,
                operation='list pull requests'
            ) from listing_failure

    def assign(self, pull_request: PullRequest) -> None:
        if not pull_request.assignees:
            return

        try:
            record = self._repository.get_issue(number=pull_request.number)
            record.add_to_assignees(*(assignee.value for assignee in pull_request.assignees))
        except GithubException as assignment_failure:
            raise GitHubRequestFailed(
                status=assignment_failure.status,
                operation='assign a pull request'
            ) from assignment_failure

        self._journal.record(
            entry=JournalEntry(
                kind=ItemKind.PULL_REQUEST,
                number=pull_request.number,
                assignees=tuple(assignee.login for assignee in record.assignees)
            )
        )
