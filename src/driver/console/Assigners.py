import logging

from src.application.commands.AssignIssues import AssignIssues
from src.application.commands.AssignPullRequestIssue import AssignPullRequestIssue
from src.application.commands.AssignPullRequests import AssignPullRequests
from src.application.domain.exceptions.DomainException import DomainException
from src.application.handlers.AssignIssueHandler import AssignIssueHandler
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler
from src.application.handlers.AssignPullRequestIssueHandler import AssignPullRequestIssueHandler
from src.driver.console.models.AssigneeOptions import AssigneeOptions
from src.driver.console.models.Request import Request
from src.driver.console.models.Result import Result
from src.driver.exceptions.InvalidAssigneeOptions import InvalidAssigneeOptions


class Assigners:

    def __init__(
            self,
            logger: logging.Logger,
            pull_handler: AssignPullRequestHandler,
            issue_handler: AssignIssueHandler,
            pull_issue_handler: AssignPullRequestIssueHandler
    ) -> None:
        self.__logger = logger
        self.__pull_handler = pull_handler
        self.__issue_handler = issue_handler
        self.__pull_issue_handler = pull_issue_handler

    def execute(self, request: Request) -> Result:
        try:
            assignee_options = AssigneeOptions(request.assignment_options)

            actor = request.actor
            assignees = request.assignees
            no_assignees = request.allow_no_assignees
            allow_self_assign = request.allow_self_assign

            if assignee_options.is_pull_request_and_issue():
                command = AssignPullRequestIssue(
                    actor=actor,
                    assignees=assignees,
                    allow_self_assign=allow_self_assign,
                    allow_no_assignees=no_assignees
                )
                self.__pull_issue_handler.handle(command=command)

            if assignee_options.is_pull_request_only():
                command = AssignPullRequests(
                    actor=actor,
                    assignees=assignees,
                    allow_self_assign=allow_self_assign,
                    allow_no_assignees=no_assignees
                )
                self.__pull_handler.handle(command=command)

            if assignee_options.is_issue_only():
                command = AssignIssues(
                    actor=actor,
                    assignees=assignees,
                    allow_self_assign=allow_self_assign,
                    allow_no_assignees=no_assignees
                )
                self.__issue_handler.handle(command=command)

            return Result.success()

        except InvalidAssigneeOptions as exception:
            self.__logger.error(str(exception))
            return Result.configuration_missing()

        except DomainException as exception:
            self.__logger.error(str(exception))
            return Result.assignment_failure()

        except Exception as exception:
            self.__logger.error(str(exception))
            return Result.unexpected_failure()
