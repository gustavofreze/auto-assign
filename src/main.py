import logging
import sys
import time

from src.driven.settings import GITHUB_ACTOR, ASSIGNMENT_OPTIONS, ASSIGNEES, ALLOW_SELF_ASSIGN, ALLOW_NO_ASSIGNEES
from src.driver.console.ExitCode import ExitCode
from src.driver.console.Request import Request
from src.starter.Dependencies import Dependencies


def main() -> ExitCode:
    time.tzset()
    logger = logging.getLogger(__name__)

    try:
        dependencies = Dependencies()
        dependencies.init_resources()

        request = Request(
            actor=GITHUB_ACTOR,
            assignees=ASSIGNEES,
            allow_self_assign=ALLOW_SELF_ASSIGN,
            allow_no_assignees=ALLOW_NO_ASSIGNEES,
            assignment_options=ASSIGNMENT_OPTIONS
        )

        assigners = dependencies.assigners()

        return assigners.execute(request=request)

    except EnvironmentError as exception:
        logger.error(str(exception))
        return ExitCode.CONFIGURATION_MISSING

    except Exception as exception:
        logger.error(str(exception))
        return ExitCode.UNEXPECTED_FAILURE


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code.value)
