import sys
import time

from src.driver.console.ExitCode import ExitCode
from src.starter.Dependencies import Dependencies


def main() -> ExitCode:
    time.tzset()

    dependencies = Dependencies()
    dependencies.init_resources()

    assigners = dependencies.assigners()
    return assigners.execute()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code.value)
