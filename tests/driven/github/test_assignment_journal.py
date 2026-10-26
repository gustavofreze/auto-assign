from src.driven.github.assignment_journal import AssignmentJournal
from src.driven.github.item_kind import ItemKind
from src.driven.github.journal_entry import JournalEntry


def journal_with_three_entries() -> AssignmentJournal:
    journal = AssignmentJournal()
    journal.record(entry=JournalEntry(kind=ItemKind.ISSUE, number=1, assignees=('alice',)))
    journal.record(entry=JournalEntry(kind=ItemKind.PULL_REQUEST, number=7, assignees=('alice', 'bob')))
    journal.record(entry=JournalEntry(kind=ItemKind.ISSUE, number=3, assignees=('bob',)))

    return journal


def test_issues_when_items_were_assigned_then_only_the_issues_are_listed_in_order() -> None:
    # Given a journal holding two assigned issues and one assigned pull request
    journal = journal_with_three_entries()

    # When the assigned issues are read
    issues = journal.issues()

    # Then each issue is listed with its assignees, in recording order
    assert issues == [{'number': 1, 'assignees': ['alice']}, {'number': 3, 'assignees': ['bob']}]


def test_pull_requests_when_items_were_assigned_then_only_the_pull_requests_are_listed() -> None:
    # Given a journal holding two assigned issues and one assigned pull request
    journal = journal_with_three_entries()

    # When the assigned pull requests are read
    pull_requests = journal.pull_requests()

    # Then the pull request is listed with its assignees
    assert pull_requests == [{'number': 7, 'assignees': ['alice', 'bob']}]


def test_issues_and_pull_requests_when_nothing_was_assigned_then_both_are_empty() -> None:
    # Given an empty journal
    journal = AssignmentJournal()

    # When the assigned issues and pull requests are read
    assigned = (journal.issues(), journal.pull_requests())

    # Then both lists are empty
    assert assigned == ([], [])


def test_summary_when_items_were_assigned_then_it_tabulates_one_row_per_item_in_order() -> None:
    # Given a journal holding two assigned issues and one assigned pull request
    journal = journal_with_three_entries()

    # When the step summary is read
    summary = journal.summary()

    # Then the summary holds a table with one row per assigned item, in recording order
    assert summary == (
        '### Auto assign\n\n'
        '| Item | Assignees |\n'
        '|:-----|:----------|\n'
        '| Issue #1 | alice |\n'
        '| Pull request #7 | alice, bob |\n'
        '| Issue #3 | bob |\n'
    )


def test_summary_when_nothing_was_assigned_then_it_says_so() -> None:
    # When the step summary of an empty journal is read
    summary = AssignmentJournal().summary()

    # Then the summary states that nothing was assigned
    assert summary == '### Auto assign\n\nNothing was assigned.\n'
