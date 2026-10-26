from abc import ABC, abstractmethod

from src.application.domain.models.commons.logins import Logins


class Assignees(ABC):
    """Members the repository accepts as assignees."""

    @abstractmethod
    def assignable(self, logins: Logins) -> Logins:
        """Selects the logins the repository accepts as assignees, keeping their order.

        :param logins: The logins requested as assignees.
        :returns: The requested logins the repository accepts.
        """
