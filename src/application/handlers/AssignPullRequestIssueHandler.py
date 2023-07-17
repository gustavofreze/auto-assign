from src.application.commands.AssignPullRequestIssue import AssignPullRequestIssue
from src.application.ports.inbound.CommandHandler import CommandHandler
from src.application.ports.outbound.Assignees import Assignees
from src.application.ports.outbound.Issues import Issues
from src.application.ports.outbound.PullRequests import PullRequests


class AssignPullRequestIssueHandler(CommandHandler):

    def __init__(self, pulls: PullRequests, issues: Issues, assignees: Assignees) -> None:
        self.__pulls = pulls
        self.__issues = issues
        self.__assignees = assignees

    def handle(self, command: AssignPullRequestIssue):
        assignees = self.__assignees.exists(assignees=command.assignees)

        pulls = self.__pulls.all()
        issues = self.__issues.all()

        for pull in pulls:
            assigned_pull = pull.assign(
                actor=command.actor,
                assignees=assignees,
                allow_self_assign=command.allow_self_assign,
                allow_no_assignees=command.allow_no_assignees
            )
            self.__pulls.apply(assigned_pull=assigned_pull)

        for issue in issues:
            assigned_issue = issue.assign(
                actor=command.actor,
                assignees=assignees,
                allow_self_assign=command.allow_self_assign,
                allow_no_assignees=command.allow_no_assignees
            )
            self.__issues.apply(assigned_issue=assigned_issue)
