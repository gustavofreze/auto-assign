from enum import IntEnum


class ExitCode(IntEnum):
    """Enumeration of possible exit codes for the application."""

    SUCCESS = 0
    """The operation completed successfully without any errors."""

    UNEXPECTED_FAILURE = 1
    """A non-recoverable or unhandled failure occurred during execution."""

    CONFIGURATION_MISSING = 2
    """Required environment variables or configuration values were not provided."""

    ASSIGNMENT_NOT_POSSIBLE = 3
    """The assignment could not be completed due to invalid conditions."""
