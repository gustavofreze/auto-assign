from src.application.domain.exceptions.DomainException import DomainException


class MissingAssignees(DomainException):

    def __init__(self) -> None:
        self.message = 'Missing assignees.'
        super().__init__(message=self.message)
