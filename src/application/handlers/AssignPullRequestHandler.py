from src.application.commands.AssignPullRequests import AssignPullRequests
from src.application.ports.inbound.CommandHandler import CommandHandler
from src.application.ports.outbound.Assignees import Assignees
from src.application.ports.outbound.PullRequests import PullRequests


class AssignPullRequestHandler(CommandHandler):

    def __init__(self, pulls: PullRequests, assignees: Assignees) -> None:
        self.__pulls = pulls
        self.__assignees = assignees

    def handle(self, command: AssignPullRequests):
        assignees = self.__assignees.exists(assignees=command.assignees)

        pulls = self.__pulls.all()

        for pull in pulls:
            assigned_pull = pull.assign(
                actor=command.actor,
                assignees=assignees,
                allow_self_assign=command.allow_self_assign,
                allow_no_assignees=command.allow_no_assignees
            )
            self.__pulls.apply(assigned_pull=assigned_pull)
