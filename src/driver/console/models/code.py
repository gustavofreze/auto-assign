from enum import IntEnum
from typing import final


@final
class Code(IntEnum):
    SUCCESS = 0
    UNEXPECTED_FAILURE = 1
    ASSIGNMENT_FAILURE = 2
    CONFIGURATION_MISSING = 3
