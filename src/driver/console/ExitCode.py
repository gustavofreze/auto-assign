from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes used by the assignment process."""

    SUCCESS = 0
    """Execution completed successfully."""

    UNEXPECTED_FAILURE = 1
    """An unexpected error occurred during execution."""

    ASSIGNMENT_FAILURE = 2
    """Failed to assign pull requests or issues."""

    CONFIGURATION_MISSING = 3
    """A required configuration value is missing."""
