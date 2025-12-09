import sys
import time

from driver.console.ExitCode import ExitCode
from src.starter.Dependencies import Dependencies


def main() -> ExitCode:
    time.tzset()

    dependencies = Dependencies()
    dependencies.init_resources()

    assigners = dependencies.assigners()
    return assigners.execute()


if __name__ == '__main__':
    sys.exit(int(main()))
