from dataclasses import dataclass
from typing import final

from src.application.domain.models.commons.login import Login


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Eligibility:
    skip_bots: bool
    skip_drafts: bool

    def excludes(self, author: Login, draft: bool) -> bool:
        return (self.skip_bots and author.is_bot()) or (self.skip_drafts and draft)
