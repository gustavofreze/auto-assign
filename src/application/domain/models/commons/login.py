from dataclasses import dataclass
from typing import final

from src.application.domain.exceptions.login_cannot_be_empty import LoginCannotBeEmpty

BOT_SUFFIX = '[bot]'


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Login:
    value: str

    def __post_init__(self) -> None:
        if self.value.strip() == '':
            raise LoginCannotBeEmpty()

    def is_bot(self) -> bool:
        return self.value.endswith(BOT_SUFFIX)
