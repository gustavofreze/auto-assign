from dependency_injector.containers import DeclarativeContainer, providers
from github import Github
from github.Repository import Repository

from src.application.handlers.AssignIssueHandler import AssignIssueHandler
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler
from src.application.handlers.AssignPullRequestIssueHandler import AssignPullRequestIssueHandler
from src.driven.assignees.Adapter import Adapter as AssigneesAdapter
from src.driven.issues.Adapter import Adapter as IssuesAdapter
from src.driven.pull_requests.Adapter import Adapter as PullRequestAdapter
from src.driven.settings import GITHUB_TOKEN, GITHUB_REPOSITORY
from src.driver.console.Assigners import Assigners


class Dependencies(DeclarativeContainer):
    client = Github(login_or_token=GITHUB_TOKEN)
    repository: Repository = client.get_repo(full_name_or_id=GITHUB_REPOSITORY)

    assignees = providers.Singleton(AssigneesAdapter, repository=repository)
    pull_adapter = providers.Singleton(PullRequestAdapter, repository=repository)
    issues_adapter = providers.Singleton(IssuesAdapter, repository=repository)

    pull_handler = providers.Factory(AssignPullRequestHandler, pulls=pull_adapter, assignees=assignees)
    issue_handler = providers.Factory(AssignIssueHandler, issues=issues_adapter, assignees=assignees)
    pull_issue_handler = providers.Factory(AssignPullRequestIssueHandler, pulls=pull_handler, issues=issue_handler)

    assigners = providers.Singleton(
        Assigners,
        pull_handler=pull_handler,
        issue_handler=issue_handler,
        pull_issue_handler=pull_issue_handler
    )
