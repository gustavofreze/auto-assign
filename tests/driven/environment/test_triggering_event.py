import json
from pathlib import Path

import pytest

from src.driven.environment.triggering_event import TriggeringEvent
from src.driven.environment.triggering_event_unreadable import TriggeringEventUnreadable


@pytest.mark.parametrize(
    ids=['issue opened', 'pull request opened', 'comment on a pull request', 'manual dispatch', 'not an object'],
    argnames=['payload', 'expected'],
    argvalues=[
        ({'issue': {'number': 3}}, TriggeringEvent(issue_numbers=(3,), pull_request_numbers=())),
        ({'pull_request': {'number': 5}}, TriggeringEvent(issue_numbers=(), pull_request_numbers=(5,))),
        ({'issue': {'number': 9, 'pull_request': {}}}, TriggeringEvent(issue_numbers=(), pull_request_numbers=(9,))),
        ({'inputs': {}}, TriggeringEvent.repository_scan()),
        ([], TriggeringEvent.repository_scan())
    ]
)
def test_from_payload_when_the_event_is_read_then_it_targets_the_triggering_item(
        payload: object,
        expected: TriggeringEvent
) -> None:
    # When the event payload is read
    event = TriggeringEvent.from_payload(payload=payload)

    # Then the event targets the item that triggered the run, or the whole repository
    assert event == expected


def test_from_file_when_the_runner_provides_an_event_file_then_its_payload_is_read(tmp_path: Path) -> None:
    # Given an event file describing an opened issue
    event_file = tmp_path / 'event.json'
    event_file.write_text(json.dumps({'issue': {'number': 3}}), encoding='utf-8')

    # When the event is read from that file
    event = TriggeringEvent.from_file(path=event_file.as_posix())

    # Then the event targets that issue
    assert event == TriggeringEvent(issue_numbers=(3,), pull_request_numbers=())


def test_from_file_when_no_event_file_is_provided_then_the_whole_repository_is_targeted() -> None:
    # When the event is read without a file
    event = TriggeringEvent.from_file(path='')

    # Then the whole repository is targeted
    assert event == TriggeringEvent.repository_scan()


def test_from_file_when_the_event_file_does_not_exist_then_triggering_event_unreadable_is_raised(
        tmp_path: Path
) -> None:
    # Then reading fails with the translated failure
    with pytest.raises(TriggeringEventUnreadable):
        # When the event is read from a path that holds no file
        TriggeringEvent.from_file(path=(tmp_path / 'absent.json').as_posix())


def test_from_file_when_the_event_file_holds_no_json_then_triggering_event_unreadable_is_raised(
        tmp_path: Path
) -> None:
    # Given an event file holding text that is not JSON
    event_file = tmp_path / 'event.json'
    event_file.write_text('not json', encoding='utf-8')

    # Then reading fails with the translated failure
    with pytest.raises(TriggeringEventUnreadable):
        # When the event is read from that file
        TriggeringEvent.from_file(path=event_file.as_posix())
