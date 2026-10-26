import logging
import os
from collections.abc import Mapping

from src.dependencies import Dependencies
from src.driven.environment.action_output import ActionOutput
from src.driven.environment.action_settings import ActionSettings
from src.driven.environment.missing_action_input import MissingActionInput
from src.driven.environment.triggering_event_unreadable import TriggeringEventUnreadable
from src.driven.github.assignment_journal import AssignmentJournal
from src.driver.console.annotation_formatter import AnnotationFormatter
from src.driver.console.models.request import Request
from src.driver.console.models.result import Result

LOGGER = logging.getLogger('auto-assign')


def run(environment: Mapping[str, str], journal: AssignmentJournal) -> Result:
    try:
        settings = ActionSettings.from_environment(environment=environment)
    except (MissingActionInput, TriggeringEventUnreadable) as invalid_configuration:
        LOGGER.exception(str(invalid_configuration), exc_info=False)
        return Result.configuration_missing(message=str(invalid_configuration))
    except Exception as settings_failure:
        LOGGER.exception(str(settings_failure))
        return Result.unexpected_failure(message=str(settings_failure))

    try:
        assigners = Dependencies(settings=settings, journal=journal).assigners()
    except Exception as wiring_failure:
        LOGGER.exception(str(wiring_failure))
        return Result.unexpected_failure(message=str(wiring_failure))

    request = Request(
        actor=settings.actor,
        assignees=settings.assignees,
        skip_bots=settings.preferences.skip_bots,
        skip_drafts=settings.preferences.skip_drafts,
        assign_author=settings.preferences.assign_author,
        allow_self_assign=settings.preferences.allow_self_assign,
        allow_no_assignees=settings.preferences.allow_no_assignees,
        assignment_options=settings.assignment_options
    )

    return assigners.assign(request=request)


if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(AnnotationFormatter())
    LOGGER.addHandler(handler)

    output_path = os.environ.get('GITHUB_OUTPUT', '')

    if output_path == '':
        LOGGER.warning('GITHUB_OUTPUT is not set, so the action outputs are not written.')

    assignment_journal = AssignmentJournal()
    result = run(environment=os.environ, journal=assignment_journal)

    ActionOutput(
        output_path=output_path,
        summary_path=os.environ.get('GITHUB_STEP_SUMMARY', '')
    ).write(
        outputs={
            'result': result.to_json(
                issues=assignment_journal.issues(),
                pull_requests=assignment_journal.pull_requests()
            )
        },
        summary=assignment_journal.summary()
    )
