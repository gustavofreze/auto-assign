import sys
import time

from src.driven.settings import GITHUB_ACTOR, ASSIGNMENT_OPTIONS, ASSIGNEES, ALLOW_SELF_ASSIGN, ALLOW_NO_ASSIGNEES
from src.driver.console.ExitCode import ExitCode
from src.driver.console.Request import Request
from src.starter.Dependencies import Dependencies


def main() -> ExitCode:
    time.tzset()

    dependencies = Dependencies()
    dependencies.init_resources()

    request = Request(
        actor=GITHUB_ACTOR,
        options=ASSIGNMENT_OPTIONS,
        assignees=ASSIGNEES,
        allow_self_assign=ALLOW_SELF_ASSIGN,
        allow_no_assignees=ALLOW_NO_ASSIGNEES
    )

    assigners = dependencies.assigners()
    return assigners.execute(request)


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code.value)
