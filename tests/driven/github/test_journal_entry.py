import pytest

from src.driven.github.item_kind import ItemKind
from src.driven.github.journal_entry import JournalEntry


@pytest.mark.parametrize(
    ids=['issue with one assignee', 'pull request with two assignees'],
    argnames=['entry', 'expected'],
    argvalues=[
        (JournalEntry(kind=ItemKind.ISSUE, number=1, assignees=('alice',)), '| Issue #1 | alice |\n'),
        (
            JournalEntry(kind=ItemKind.PULL_REQUEST, number=7, assignees=('alice', 'bob')),
            '| Pull request #7 | alice, bob |\n'
        )
    ]
)
def test_to_row_when_an_entry_is_tabulated_then_the_row_names_the_item_and_its_assignees(
        entry: JournalEntry,
        expected: str
) -> None:
    # When the entry is turned into a summary row
    row = entry.to_row()

    # Then the row names the kind, the number, and the assignees in order
    assert row == expected


def test_to_payload_when_an_entry_is_reported_then_it_carries_the_number_and_the_assignees() -> None:
    # Given an entry for a pull request assigned to two logins
    entry = JournalEntry(kind=ItemKind.PULL_REQUEST, number=7, assignees=('alice', 'bob'))

    # When the entry is turned into its output payload
    payload = entry.to_payload()

    # Then the payload carries the number and the assignees in order
    assert payload == {'number': 7, 'assignees': ['alice', 'bob']}
