import logging

import pytest

from src.driver.console.annotation_formatter import AnnotationFormatter


@pytest.mark.parametrize(
    ids=['error', 'warning', 'info', 'debug'],
    argnames=['level', 'expected'],
    argvalues=[
        (logging.ERROR, '::error::Assignees are required.'),
        (logging.WARNING, '::warning::Assignees are required.'),
        (logging.INFO, 'Assignees are required.'),
        (logging.DEBUG, 'Assignees are required.')
    ]
)
def test_format_when_a_record_is_formatted_then_only_errors_and_warnings_become_annotations(
        level: int,
        expected: str
) -> None:
    # When a record of the given level is formatted
    line = AnnotationFormatter().format(
        record=logging.makeLogRecord({'levelno': level, 'msg': 'Assignees are required.'})
    )

    # Then errors and warnings carry their workflow annotation prefix, and other levels stay plain
    assert line == expected
