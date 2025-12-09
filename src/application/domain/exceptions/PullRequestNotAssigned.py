from application.domain.exceptions.DomainException import DomainException


class PullRequestNotAssigned(DomainException):

    def __init__(self, assignee: str) -> None:
        self.message = f"Not allowed to assign pull requests to self <{assignee}>."
        super().__init__(self.message)
