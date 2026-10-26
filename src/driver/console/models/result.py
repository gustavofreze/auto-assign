import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import final

from src.driver.console.models.code import Code

UNEXPECTED_FAILURE_MESSAGE = 'An unexpected error occurred.'


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Result:
    code: Code
    message: str

    @staticmethod
    def success() -> Result:
        return Result(code=Code.SUCCESS, message='')

    @staticmethod
    def unexpected_failure(message: str) -> Result:
        return Result(code=Code.UNEXPECTED_FAILURE, message=message or UNEXPECTED_FAILURE_MESSAGE)

    @staticmethod
    def assignment_failure(message: str) -> Result:
        return Result(code=Code.ASSIGNMENT_FAILURE, message=message)

    @staticmethod
    def configuration_missing(message: str) -> Result:
        return Result(code=Code.CONFIGURATION_MISSING, message=message)

    def to_json(self, issues: Sequence[Mapping[str, object]], pull_requests: Sequence[Mapping[str, object]]) -> str:
        assigned = (
            f'Assigned {counted(total=len(issues), noun="issue")} '
            f'and {counted(total=len(pull_requests), noun="pull request")}.'
        )

        return json.dumps({
            'code': self.code.value,
            'status': self.code.name,
            'message': assigned if self.code is Code.SUCCESS else self.message,
            'issues': list(issues),
            'pull_requests': list(pull_requests)
        })


def counted(total: int, noun: str) -> str:
    return f'{total} {noun}' if total == 1 else f'{total} {noun}s'
