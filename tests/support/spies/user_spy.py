from typing import final


@final
class UserSpy:

    def __init__(self, login: str) -> None:
        self.login = login
