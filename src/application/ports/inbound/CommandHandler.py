from abc import ABC, abstractmethod

from src.application.commands.Command import Command


class CommandHandler(ABC):

    @abstractmethod
    def handle(self, command: Command):
        """
        Executes a use case for a command.

        :param command: The command to be handled.
        :type command: Command

        :raises MissingAssignees: If it is missing assignees.
        """
