import logging

from application.domain.exceptions.DomainException import DomainException
from driver.console.AssigneeOptions import AssigneeOptions
from driver.console.ExitCode import ExitCode
from driver.exceptions.InvalidAssigneeOptions import InvalidAssigneeOptions
from src.application.commands.AssignIssues import AssignIssues
from src.application.commands.AssignPullRequestIssue import AssignPullRequestIssue
from src.application.commands.AssignPullRequests import AssignPullRequests
from src.application.handlers.AssignIssueHandler import AssignIssueHandler
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler
from src.application.handlers.AssignPullRequestIssueHandler import AssignPullRequestIssueHandler
from src.driven.settings import (ASSIGNMENT_OPTIONS, ASSIGNEES, ALLOW_NO_ASSIGNEES,
                                 ALLOW_SELF_ASSIGN, GITHUB_ACTOR)


class Assigners:

    def __init__(
            self,
            pull_handler: AssignPullRequestHandler,
            issue_handler: AssignIssueHandler,
            pull_issue_handler: AssignPullRequestIssueHandler,
            logger: logging.Logger
    ) -> None:
        self.__pull_handler = pull_handler
        self.__issue_handler = issue_handler
        self.__pull_issue_handler = pull_issue_handler
        self.__logger = logger

    def execute(self) -> ExitCode:
        actor = GITHUB_ACTOR
        options = ASSIGNMENT_OPTIONS
        assignees = ASSIGNEES
        allow_self_assign = ALLOW_SELF_ASSIGN
        allow_no_assignees = ALLOW_NO_ASSIGNEES

        try:
            assignee_options = AssigneeOptions(options)

            if assignee_options.is_pull_request_and_issue():
                command = AssignPullRequestIssue(
                    actor=actor,
                    assignees=assignees,
                    allow_self_assign=allow_self_assign,
                    allow_no_assignees=allow_no_assignees
                )
                self.__pull_issue_handler.handle(command=command)

            if assignee_options.is_pull_request_only():
                command = AssignPullRequests(
                    actor=actor,
                    assignees=assignees,
                    allow_self_assign=allow_self_assign,
                    allow_no_assignees=allow_no_assignees
                )
                self.__pull_handler.handle(command=command)

            if assignee_options.is_issue_only():
                command = AssignIssues(
                    actor=actor,
                    assignees=assignees,
                    allow_self_assign=allow_self_assign,
                    allow_no_assignees=allow_no_assignees
                )
                self.__issue_handler.handle(command=command)

            return ExitCode.SUCCESS

        except InvalidAssigneeOptions as exception:
            self.__logger.error(exception.message)
            return ExitCode.MISSING_ENVIRONMENT

        except DomainException as exception:
            self.__logger.error(exception.message)
            return ExitCode.MISSING_ENVIRONMENT

        except Exception as exception:
            self.__logger.error(str(exception))
            return ExitCode.UNEXPECTED_ERROR
