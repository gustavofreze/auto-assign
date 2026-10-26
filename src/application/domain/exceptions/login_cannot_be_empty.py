from typing import final

from src.application.domain.exceptions.domain_exception import DomainException


@final
class LoginCannotBeEmpty(DomainException):

    def __init__(self) -> None:
        super().__init__(message='Login cannot be empty.')
