from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Request:
    actor: str
    assignees: tuple[str, ...]
    skip_bots: bool
    skip_drafts: bool
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool
    assignment_options: tuple[str, ...]
