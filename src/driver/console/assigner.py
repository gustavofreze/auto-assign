from abc import ABC, abstractmethod

from src.driver.console.models.request import Request


class Assigner(ABC):
    """Assignment of one kind of repository item requested by the action."""

    @abstractmethod
    def assign(self, request: Request) -> None:
        """Assigns the items of its kind according to the action request.

        :param request: The action request carrying the actor, the assignees, and the self-assignment flags.
        """
