from collections.abc import Iterable
from enum import StrEnum
from typing import final

from src.driver.exceptions.invalid_assignment_options import InvalidAssignmentOptions

ISSUE_OPTION = 'ISSUE'
PULL_REQUEST_OPTION = 'PULL_REQUEST'


@final
class AssignmentKind(StrEnum):
    ISSUES = 'ISSUES'
    PULL_REQUESTS = 'PULL_REQUESTS'
    PULL_REQUESTS_AND_ISSUES = 'PULL_REQUESTS_AND_ISSUES'

    @staticmethod
    def from_options(options: Iterable[str]) -> AssignmentKind:
        requested = frozenset(options)
        kinds = {
            frozenset({ISSUE_OPTION}): AssignmentKind.ISSUES,
            frozenset({PULL_REQUEST_OPTION}): AssignmentKind.PULL_REQUESTS,
            frozenset({ISSUE_OPTION, PULL_REQUEST_OPTION}): AssignmentKind.PULL_REQUESTS_AND_ISSUES
        }
        kind = kinds.get(requested)

        if kind is None:
            raise InvalidAssignmentOptions(options=requested)

        return kind
