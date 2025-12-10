from typing import Iterable, FrozenSet

from src.driver.exceptions.InvalidAssigneeOptions import InvalidAssigneeOptions


class AssigneeOptions:
    ISSUE = "ISSUE"
    PULL_REQUEST = "PULL_REQUEST"
    PULL_REQUEST_ISSUE = "PULL_REQUEST_ISSUE"

    def __init__(self, raw_options: Iterable[str]) -> None:
        self.__normalized_options: FrozenSet[str] = frozenset(raw_options or [])
        self.__assignment_kind = self.__determine_assignment_kind()

    def __determine_assignment_kind(self) -> str:
        decision_table = {
            frozenset({self.ISSUE}): self.ISSUE,
            frozenset({self.PULL_REQUEST}): self.PULL_REQUEST,
            frozenset({self.ISSUE, self.PULL_REQUEST}): self.PULL_REQUEST_ISSUE,
        }

        assignment_kind = decision_table.get(self.__normalized_options)

        if assignment_kind is None:
            raise InvalidAssigneeOptions(self.__normalized_options)

        return assignment_kind

    def is_issue_only(self) -> bool:
        return self.__assignment_kind == self.ISSUE

    def is_pull_request_only(self) -> bool:
        return self.__assignment_kind == self.PULL_REQUEST

    def is_pull_request_and_issue(self) -> bool:
        return self.__assignment_kind == self.PULL_REQUEST_ISSUE
