from typing import Iterable


class InvalidAssigneeOptions(RuntimeError):

    def __init__(self, invalid_options: Iterable[str]) -> None:
        self.message = f"Invalid assignment options <{sorted(invalid_options)}>."
        super().__init__(self.message)
