from enum import StrEnum
from typing import final


@final
class ItemKind(StrEnum):
    ISSUE = 'Issue'
    PULL_REQUEST = 'Pull request'
