import json
from dataclasses import dataclass
from typing import final

from src.driven.environment.triggering_event_unreadable import TriggeringEventUnreadable


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class TriggeringEvent:
    issue_numbers: tuple[int, ...] | None
    pull_request_numbers: tuple[int, ...] | None

    @staticmethod
    def repository_scan() -> TriggeringEvent:
        return TriggeringEvent(issue_numbers=None, pull_request_numbers=None)

    @staticmethod
    def from_file(path: str) -> TriggeringEvent:
        if path == '':
            return TriggeringEvent.repository_scan()

        try:
            with open(file=path, encoding='utf-8') as event_file:
                payload: object = json.load(event_file)
        except (OSError, ValueError) as read_failure:
            raise TriggeringEventUnreadable(path=path) from read_failure

        return TriggeringEvent.from_payload(payload=payload)

    @staticmethod
    def from_payload(payload: object) -> TriggeringEvent:
        if not isinstance(payload, dict):
            return TriggeringEvent.repository_scan()

        pull_request = payload.get('pull_request')

        if isinstance(pull_request, dict) and isinstance(pull_request.get('number'), int):
            return TriggeringEvent(issue_numbers=(), pull_request_numbers=(pull_request['number'],))

        issue = payload.get('issue')

        if not isinstance(issue, dict) or not isinstance(issue.get('number'), int):
            return TriggeringEvent.repository_scan()

        if 'pull_request' in issue:
            return TriggeringEvent(issue_numbers=(), pull_request_numbers=(issue['number'],))

        return TriggeringEvent(issue_numbers=(issue['number'],), pull_request_numbers=())
