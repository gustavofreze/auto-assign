import logging
from typing import final

ANNOTATIONS = {logging.ERROR: '::error::', logging.WARNING: '::warning::'}


@final
class AnnotationFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        return ANNOTATIONS.get(record.levelno, '') + super().format(record)
