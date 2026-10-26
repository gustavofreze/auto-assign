from typing import final


@final
class GitHubRequestFailed(Exception):

    def __init__(self, status: int, operation: str) -> None:
        super().__init__(f'GitHub request to {operation} failed with status <{status}>.')
