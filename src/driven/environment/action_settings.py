from collections.abc import Mapping
from dataclasses import dataclass
from typing import final

from src.driven.environment.assignment_preferences import AssignmentPreferences
from src.driven.environment.missing_action_input import MissingActionInput
from src.driven.environment.triggering_event import TriggeringEvent

ENABLED = 'true'
DISABLED = 'false'
ISSUE_OPTION = 'ISSUE'
REQUIRED_VARIABLES = ('GITHUB_ACTOR', 'GITHUB_REPOSITORY', 'INPUT_ASSIGNEES', 'INPUT_GITHUB_TOKEN')


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ActionSettings:
    actor: str
    event: TriggeringEvent
    assignees: tuple[str, ...]
    repository: str
    preferences: AssignmentPreferences
    github_token: str
    assignment_options: tuple[str, ...]

    @staticmethod
    def from_environment(environment: Mapping[str, str]) -> ActionSettings:
        missing = tuple(
            variable for variable in REQUIRED_VARIABLES if read(environment=environment, variable=variable) == ''
        )

        if missing:
            raise MissingActionInput(variables=missing)

        return ActionSettings(
            actor=read(environment=environment, variable='GITHUB_ACTOR'),
            event=TriggeringEvent.from_file(path=read(environment=environment, variable='GITHUB_EVENT_PATH')),
            assignees=listed(raw=read(environment=environment, variable='INPUT_ASSIGNEES')),
            repository=read(environment=environment, variable='GITHUB_REPOSITORY'),
            preferences=AssignmentPreferences(
                skip_bots=enabled(raw=optional(environment=environment, variable='INPUT_SKIP_BOTS', default=DISABLED)),
                skip_drafts=enabled(
                    raw=optional(environment=environment, variable='INPUT_SKIP_DRAFTS', default=DISABLED)
                ),
                assign_author=enabled(
                    raw=optional(environment=environment, variable='INPUT_ASSIGN_AUTHOR', default=DISABLED)
                ),
                allow_self_assign=enabled(
                    raw=optional(environment=environment, variable='INPUT_ALLOW_SELF_ASSIGN', default=ENABLED)
                ),
                allow_no_assignees=enabled(
                    raw=optional(environment=environment, variable='INPUT_ALLOW_NO_ASSIGNEES', default=DISABLED)
                )
            ),
            github_token=read(environment=environment, variable='INPUT_GITHUB_TOKEN'),
            assignment_options=listed(
                raw=optional(environment=environment, variable='INPUT_ASSIGNMENT_OPTIONS', default=ISSUE_OPTION)
            )
        )


def read(environment: Mapping[str, str], variable: str) -> str:
    return environment.get(variable, '').strip()


def optional(environment: Mapping[str, str], variable: str, default: str) -> str:
    return read(environment=environment, variable=variable) or default


def listed(raw: str) -> tuple[str, ...]:
    return tuple(entry.strip() for entry in raw.split(',') if entry.strip() != '')


def enabled(raw: str) -> bool:
    return raw.lower() == ENABLED
