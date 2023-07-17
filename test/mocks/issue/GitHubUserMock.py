from unittest.mock import MagicMock

from github.NamedUser import NamedUser


class GitHubUserMock(MagicMock):

    def __init__(self, login: str) -> None:
        super().__init__(spec=NamedUser)
        self.login = login
