from typing import final


@final
class TriggeringEventUnreadable(Exception):

    def __init__(self, path: str) -> None:
        super().__init__(f'The event file <{path}> cannot be read as a JSON payload.')
