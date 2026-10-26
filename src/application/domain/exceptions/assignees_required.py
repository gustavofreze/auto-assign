from typing import final

from src.application.domain.exceptions.domain_exception import DomainException


@final
class AssigneesRequired(DomainException):

    def __init__(self) -> None:
        super().__init__(message='Assignees are required.')
