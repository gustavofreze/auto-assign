from typing import final

from src.application.domain.exceptions.domain_exception import DomainException
from src.application.domain.models.commons.login import Login


@final
class SelfAssignmentNotAllowed(DomainException):

    def __init__(self, actor: Login) -> None:
        super().__init__(message=f'Not allowed to self-assign <{actor.value}>.')
