from collections.abc import Iterable
from typing import final


@final
class InvalidAssignmentOptions(Exception):

    def __init__(self, options: Iterable[str]) -> None:
        super().__init__(f'Invalid assignment options <{sorted(options)}>.')
