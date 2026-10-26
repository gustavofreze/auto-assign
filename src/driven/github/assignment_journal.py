from typing import final

from src.driven.github.item_kind import ItemKind
from src.driven.github.journal_entry import JournalEntry

SUMMARY_TITLE = '### Auto assign\n\n'
SUMMARY_HEADER = '| Item | Assignees |\n|:-----|:----------|\n'


@final
class AssignmentJournal:

    def __init__(self) -> None:
        self._entries: list[JournalEntry] = []

    def record(self, entry: JournalEntry) -> None:
        self._entries.append(entry)

    def issues(self) -> list[dict[str, object]]:
        return [entry.to_payload() for entry in self._entries if entry.kind is ItemKind.ISSUE]

    def pull_requests(self) -> list[dict[str, object]]:
        return [entry.to_payload() for entry in self._entries if entry.kind is ItemKind.PULL_REQUEST]

    def summary(self) -> str:
        if not self._entries:
            return f'{SUMMARY_TITLE}Nothing was assigned.\n'

        return SUMMARY_TITLE + SUMMARY_HEADER + ''.join(entry.to_row() for entry in self._entries)
