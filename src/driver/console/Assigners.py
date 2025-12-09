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
            pull_issue_handler: AssignPullRequestIssueHandler
    ) -> None:
        self.__pull_handler = pull_handler
        self.__issue_handler = issue_handler
        self.__pull_issue_handler = pull_issue_handler

    def execute(self):
        actor = GITHUB_ACTOR
        options = ASSIGNMENT_OPTIONS
        assignees = ASSIGNEES
        allow_self_assign = ALLOW_SELF_ASSIGN
        allow_no_assignees = ALLOW_NO_ASSIGNEES

        if 'ISSUE' in options and 'PULL_REQUEST' in options:
            command = AssignPullRequestIssue(
                actor=actor,
                assignees=assignees,
                allow_self_assign=allow_self_assign,
                allow_no_assignees=allow_no_assignees
            )
            self.__pull_issue_handler.handle(command=command)
            return

        if 'PULL_REQUEST' in options:
            command = AssignPullRequests(
                actor=actor,
                assignees=assignees,
                allow_self_assign=allow_self_assign,
                allow_no_assignees=allow_no_assignees
            )
            self.__pull_handler.handle(command=command)
            return

        command = AssignIssues(
            actor=actor,
            assignees=assignees,
            allow_self_assign=allow_self_assign,
            allow_no_assignees=allow_no_assignees
        )
        self.__issue_handler.handle(command=command)
