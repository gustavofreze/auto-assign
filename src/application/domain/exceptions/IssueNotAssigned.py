from src.application.domain.exceptions.DomainException import DomainException


class IssueNotAssigned(DomainException):

    def __init__(self, assignee: str) -> None:
        self.message = f"Not allowed to assign issues to self <{assignee}>."
        super().__init__(message=self.message)
