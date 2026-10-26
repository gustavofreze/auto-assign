from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AssignmentPreferences:
    skip_bots: bool
    skip_drafts: bool
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool
