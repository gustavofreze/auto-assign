from abc import ABC, abstractmethod
from typing import List


class Assignees(ABC):

    @abstractmethod
    def exists(self, assignees: List[str]) -> List[str]:
        """
        Verifies if all the assignees exist.

        :param assignees: A list of assignee names to verify.
        :type assignees: List[str]

        :raises NoAssigneesFound: If none of the assignees exist.
        """
