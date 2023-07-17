class PullRequestNotAssigned(RuntimeError):

    def __init__(self, assignee: str) -> None:
        self.message = f"Not allowed to assign pull requests to self <{assignee}>."
        super().__init__(self.message)
