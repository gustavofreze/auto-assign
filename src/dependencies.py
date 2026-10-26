import logging

from dependency_injector import containers, providers
from github import Auth, Github

from src.application.handlers.issues_assigning_handler import IssuesAssigningHandler
from src.application.handlers.pull_requests_and_issues_assigning_handler import PullRequestsAndIssuesAssigningHandler
from src.application.handlers.pull_requests_assigning_handler import PullRequestsAssigningHandler
from src.driven.environment.action_settings import ActionSettings
from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.github_assignees import GitHubAssignees
from src.driven.github.github_issue_records import GitHubIssueRecords
from src.driven.github.github_issues import GitHubIssues
from src.driven.github.github_pull_request_records import GitHubPullRequestRecords
from src.driven.github.github_pull_requests import GitHubPullRequests
from src.driver.console.assigners import Assigners
from src.driver.console.issues_assigner import IssuesAssigner
from src.driver.console.models.assignment_kind import AssignmentKind
from src.driver.console.pull_requests_and_issues_assigner import PullRequestsAndIssuesAssigner
from src.driver.console.pull_requests_assigner import PullRequestsAssigner

PAGE_SIZE = 100
GITHUB_API_VERSION = '2026-03-10'


class Dependencies(containers.DeclarativeContainer):
    journal = providers.Dependency(instance_of=AssignmentJournal)
    settings = providers.Dependency(instance_of=ActionSettings)

    client = providers.Singleton(
        Github,
        auth=providers.Factory(Auth.Token, token=settings.provided.github_token),
        lazy=True,
        per_page=PAGE_SIZE,
        api_version=GITHUB_API_VERSION
    )

    repository = providers.Singleton(
        lambda client, name: client.get_repo(full_name_or_id=name),
        client=client,
        name=settings.provided.repository
    )

    issue_records = providers.Singleton(
        GitHubIssueRecords,
        repository=repository,
        triggering_numbers=settings.provided.event.issue_numbers
    )

    issues = providers.Singleton(GitHubIssues, records=issue_records, journal=journal, repository=repository)

    assignees = providers.Singleton(GitHubAssignees, repository=repository)

    pull_request_records = providers.Singleton(
        GitHubPullRequestRecords,
        repository=repository,
        triggering_numbers=settings.provided.event.pull_request_numbers
    )

    pull_requests = providers.Singleton(
        GitHubPullRequests,
        records=pull_request_records,
        journal=journal,
        repository=repository
    )

    assign_issues = providers.Factory(IssuesAssigningHandler, issues=issues, assignees=assignees)

    assign_pull_requests = providers.Factory(
        PullRequestsAssigningHandler,
        assignees=assignees,
        pull_requests=pull_requests
    )

    assign_pull_requests_and_issues = providers.Factory(
        PullRequestsAndIssuesAssigningHandler,
        issues=issues,
        assignees=assignees,
        pull_requests=pull_requests
    )

    assigners = providers.Singleton(
        Assigners,
        logger=logging.getLogger('auto-assign'),
        assigners=providers.Dict({
            AssignmentKind.ISSUES: providers.Factory(IssuesAssigner, issues=assign_issues),
            AssignmentKind.PULL_REQUESTS: providers.Factory(PullRequestsAssigner, pull_requests=assign_pull_requests),
            AssignmentKind.PULL_REQUESTS_AND_ISSUES: providers.Factory(
                PullRequestsAndIssuesAssigner,
                pull_requests_and_issues=assign_pull_requests_and_issues
            )
        })
    )
