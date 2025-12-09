from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    """The operation completed successfully without any errors."""

    UNEXPECTED_ERROR = 1
    """A non-recoverable or unhandled error occurred during execution."""

    MISSING_ENVIRONMENT = 2
    """Required environment variables or configuration values were not provided."""
