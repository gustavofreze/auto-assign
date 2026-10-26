from src.driven.github.github_issue_records import GitHubIssueRecords
from tests.support.spies.record_spy import RecordSpy
from tests.support.spies.repository_spy import RepositorySpy
from tests.support.spies.user_spy import UserSpy


def two_record_repository() -> RepositorySpy:
    return RepositorySpy(
        records=(
            RecordSpy(user=UserSpy(login='dan'), draft=False, state='open', number=1, assignees=(), pull_request=None),
            RecordSpy(user=UserSpy(login='dan'), draft=False, state='open', number=2, assignees=(), pull_request=None)
        ),
        members=(),
        failure=None
    )


def test_in_scope_when_no_item_triggered_the_run_then_every_record_is_listed() -> None:
    # Given a repository with two records
    repository = two_record_repository()

    # When the records in scope are listed for a repository scan
    in_scope = GitHubIssueRecords(repository=repository, triggering_numbers=None).in_scope()

    # Then every record of the repository is listed
    assert tuple(record.number for record in in_scope) == (1, 2)

    # And the listing asks GitHub only for unassigned records
    assert repository.listed_assignee == 'none'


def test_in_scope_when_an_issue_triggered_the_run_then_only_that_record_is_listed() -> None:
    # Given a repository with two records
    repository = two_record_repository()

    # When the records in scope are listed for the run triggered by number 2
    in_scope = GitHubIssueRecords(repository=repository, triggering_numbers=(2,)).in_scope()

    # Then only the triggering record is listed
    assert tuple(record.number for record in in_scope) == (2,)
