from dataclasses import dataclass
from typing import final

from src.driven.github.item_kind import ItemKind


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class JournalEntry:
    kind: ItemKind
    number: int
    assignees: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {'number': self.number, 'assignees': list(self.assignees)}

    def to_row(self) -> str:
        return f'| {self.kind} #{self.number} | {", ".join(self.assignees)} |\n'
