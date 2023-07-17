import time

from src.starter.Dependencies import Dependencies


def main():
    time.tzset()

    dependencies = Dependencies()
    dependencies.init_resources()

    assigners = dependencies.assigners()
    assigners.execute()


if __name__ == '__main__':
    main()
