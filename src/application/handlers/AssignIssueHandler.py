from src.application.commands.AssignIssues import AssignIssues
from src.application.ports.inbound.CommandHandler import CommandHandler
from src.application.ports.outbound.Assignees import Assignees
from src.application.ports.outbound.Issues import Issues


class AssignIssueHandler(CommandHandler):

    def __init__(self, issues: Issues, assignees: Assignees) -> None:
        self.__issues = issues
        self.__assignees = assignees

    def handle(self, command: AssignIssues):
        assignees = self.__assignees.exists(assignees=command.assignees)

        issues = self.__issues.all()

        for issue in issues:
            assigned_issue = issue.assign(
                actor=command.actor,
                assignees=assignees,
                allow_self_assign=command.allow_self_assign,
                allow_no_assignees=command.allow_no_assignees
            )
            self.__issues.apply(assigned_issue=assigned_issue)
