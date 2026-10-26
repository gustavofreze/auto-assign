from collections.abc import Iterator
from dataclasses import dataclass
from typing import final

from src.application.domain.models.commons.login import Login


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Logins:
    elements: tuple[Login, ...]

    @staticmethod
    def empty() -> Logins:
        return Logins(elements=())

    @staticmethod
    def from_raw(values: tuple[str, ...]) -> Logins:
        return Logins(elements=tuple(Login(value=value) for value in values))

    def __iter__(self) -> Iterator[Login]:
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    def __contains__(self, login: object) -> bool:
        return login in self.elements

    def without(self, login: Login) -> Logins:
        return Logins(elements=tuple(element for element in self.elements if element != login))

    def shared_with(self, other: Logins) -> Logins:
        shared = frozenset(other.elements)

        return Logins(elements=tuple(element for element in self.elements if element in shared))

    def including(self, other: Logins) -> Logins:
        held = frozenset(self.elements)

        return Logins(elements=self.elements + tuple(element for element in other if element not in held))
