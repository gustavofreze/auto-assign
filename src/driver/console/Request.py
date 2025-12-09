from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Request:

    def __init__(
            self,
            actor: str,
            options: Iterable[str],
            assignees: List[str],
            allow_self_assign: bool,
            allow_no_assignees: bool
    ) -> None:
        self._actor = actor
        self._options = list(options or [])
        self._assignees = assignees
        self._allow_self_assign = allow_self_assign
        self._allow_no_assignees = allow_no_assignees

    @property
    def actor(self) -> str:
        return self._actor

    @property
    def options(self) -> List[str]:
        return self._options

    @property
    def assignees(self) -> List[str]:
        return self._assignees

    @property
    def allow_self_assign(self) -> bool:
        return self._allow_self_assign

    @property
    def allow_no_assignees(self) -> bool:
        return self._allow_no_assignees
