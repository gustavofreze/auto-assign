import logging
import time

from src.driven.settings import (
    ASSIGNEES,
    GITHUB_ACTOR,
    GITHUB_OUTPUT,
    ALLOW_SELF_ASSIGN,
    ALLOW_NO_ASSIGNEES,
    ASSIGNMENT_OPTIONS,
)
from src.driver.console.models.Request import Request
from src.driver.console.models.Result import Result
from src.starter.Dependencies import Dependencies


def main() -> Result:
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

    except Exception as exception:
        logger.error(str(exception))
        return Result.unexpected_failure()


if __name__ == '__main__':
    result = main()

    with open(file=GITHUB_OUTPUT, mode="a", encoding="utf-8") as writer:
        writer.write(f"result={result.to_json()}\n")
