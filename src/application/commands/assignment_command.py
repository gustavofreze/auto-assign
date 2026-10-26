from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AssignmentCommand:
    actor: str
    assignees: tuple[str, ...]
    skip_bots: bool
    skip_drafts: bool
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool
