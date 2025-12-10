import logging

from dependency_injector import containers, providers
from github import Github, Auth

from src.application.handlers.AssignIssueHandler import AssignIssueHandler
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler
from src.application.handlers.AssignPullRequestIssueHandler import AssignPullRequestIssueHandler
from src.driven.assignees.Adapter import Adapter as AssigneesAdapter
from src.driven.issues.Adapter import Adapter as IssuesAdapter
from src.driven.pull_requests.Adapter import Adapter as PullRequestAdapter
from src.driven.settings import GITHUB_TOKEN, GITHUB_REPOSITORY
from src.driver.console.Assigners import Assigners


class Dependencies(containers.DeclarativeContainer):
    client = providers.Singleton(
        Github,
        auth=Auth.Token(GITHUB_TOKEN),
    )

    repository = providers.Singleton(
        lambda client: client.get_repo(GITHUB_REPOSITORY),
        client=client
    )

    assignees = providers.Singleton(
        AssigneesAdapter,
        repository=repository
    )

    pull_adapter = providers.Singleton(
        PullRequestAdapter,
        repository=repository
    )

    issues_adapter = providers.Singleton(
        IssuesAdapter,
        repository=repository
    )

    pull_handler = providers.Factory(
        AssignPullRequestHandler,
        pulls=pull_adapter,
        assignees=assignees,
    )

    issue_handler = providers.Factory(
        AssignIssueHandler,
        issues=issues_adapter,
        assignees=assignees
    )

    pull_issue_handler = providers.Factory(
        AssignPullRequestIssueHandler,
        pulls=pull_handler,
        issues=issue_handler,
    )

    assigners = providers.Singleton(
        Assigners,
        logger=logging.getLogger(__name__),
        pull_handler=pull_handler,
        issue_handler=issue_handler,
        pull_issue_handler=pull_issue_handler
    )
