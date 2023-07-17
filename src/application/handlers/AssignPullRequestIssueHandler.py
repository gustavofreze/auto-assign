from src.application.commands.AssignIssues import AssignIssues
from src.application.commands.AssignPullRequestIssue import AssignPullRequestIssue
from src.application.commands.AssignPullRequests import AssignPullRequests
from src.application.handlers.AssignIssueHandler import AssignIssueHandler
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler
from src.application.ports.inbound.CommandHandler import CommandHandler


class AssignPullRequestIssueHandler(CommandHandler):

    def __init__(self, pulls: AssignPullRequestHandler, issues: AssignIssueHandler) -> None:
        self.__pulls = pulls
        self.__issues = issues

    def handle(self, command: AssignPullRequestIssue):
        assign_pull_requests = AssignPullRequests(
            actor=command.actor,
            assignees=command.assignees,
            allow_self_assign=command.allow_self_assign,
            allow_no_assignees=command.allow_no_assignees
        )
        assign_issues = AssignIssues(
            actor=command.actor,
            assignees=command.assignees,
            allow_self_assign=command.allow_self_assign,
            allow_no_assignees=command.allow_no_assignees
        )

        self.__pulls.handle(command=assign_pull_requests)
        self.__issues.handle(command=assign_issues)
