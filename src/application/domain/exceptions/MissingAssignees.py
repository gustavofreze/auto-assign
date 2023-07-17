class MissingAssignees(RuntimeError):

    def __init__(self) -> None:
        self.message = 'Missing assignees.'
        super().__init__(self.message)
