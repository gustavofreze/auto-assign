import logging
from collections.abc import Mapping
from typing import final

from src.application.domain.exceptions.domain_exception import DomainException
from src.driver.console.assigner import Assigner
from src.driver.console.models.assignment_kind import AssignmentKind
from src.driver.console.models.request import Request
from src.driver.console.models.result import Result
from src.driver.exceptions.invalid_assignment_options import InvalidAssignmentOptions


@final
class Assigners:

    def __init__(self, logger: logging.Logger, assigners: Mapping[AssignmentKind, Assigner]) -> None:
        self._logger = logger
        self._assigners = assigners

    def assign(self, request: Request) -> Result:
        try:
            kind = AssignmentKind.from_options(options=request.assignment_options)
            self._assigners[kind].assign(request=request)
        except InvalidAssignmentOptions as invalid_options:
            self._logger.exception(str(invalid_options), exc_info=False)
            return Result.configuration_missing(message=str(invalid_options))
        except DomainException as assignment_failure:
            self._logger.exception(str(assignment_failure), exc_info=False)
            return Result.assignment_failure(message=str(assignment_failure))
        except Exception as unexpected_failure:
            self._logger.exception(str(unexpected_failure))
            return Result.unexpected_failure(message=str(unexpected_failure))

        return Result.success()
