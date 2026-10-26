#!/usr/bin/env python3
"""Prose punctuation check for Markdown prose and Python comments and docstrings.

Flags the em-dash, the en-dash, the spaced double hyphen, and (Markdown only) the
semicolon used as clause separators. Fenced code, table rows, and inline code are
exempt.
"""

import re
import sys
from pathlib import Path
from typing import Final

from hooklib import python
from hooklib.core import FileUnit, Violation, read_unit, run_check

MARKDOWN_PATTERN: Final = re.compile(r"\.md$")
PYTHON_PATTERN: Final = re.compile(r"\.py$")

# Prohibited prose punctuation as clause separators. Em-dash U+2014, en-dash U+2013,
# spaced double hyphen, and (Markdown only) the semicolon.
PROSE_PUNCTUATION: Final = re.compile(r"[—–]| -- |;")
PROSE_DASHES: Final = re.compile(r"[—–]| -- ")
FENCE: Final = re.compile(r"^\s*```")
INLINE_CODE: Final = re.compile(r"`[^`]*`")


def markdown_violations(unit: FileUnit) -> tuple[Violation, ...]:
    """Markdown prose violations. Fenced code and table rows are exempt."""
    violations = []
    in_fence = False
    for number, line in enumerate(unit.text.split("\n"), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue

        if in_fence or "|" in line:
            continue

        if PROSE_PUNCTUATION.search(INLINE_CODE.sub("", line)):
            violations.append(Violation(
                line=number,
                path=unit.path,
                message=(
                    "prohibited prose punctuation (`;`, em-dash, en-dash, or ` -- `), "
                    "split the sentence or use a comma, colon, or parentheses"
                ),
            ))
    return tuple(violations)


def python_violations(unit: FileUnit) -> tuple[Violation, ...]:
    """Python comment and docstring violations. The `;` is not checked here."""
    prose = python.comments(unit.text) + python.docstrings(unit.text)
    return tuple(
        Violation(
            line=fragment.line,
            path=unit.path,
            message="prohibited prose punctuation (em-dash, en-dash, or ` -- `) in a comment or docstring",
        )
        for fragment in prose
        if PROSE_DASHES.search(INLINE_CODE.sub("", fragment.text))
    )


def punctuation_violations(unit: FileUnit) -> tuple[Violation, ...]:
    """Punctuation violations for one file, routed by kind: Markdown or Python."""
    if MARKDOWN_PATTERN.search(unit.path):
        return markdown_violations(unit)
    return python_violations(unit)


def in_scope(path: Path) -> bool:
    """Whether the path is any Markdown file, or a Python module under src/ or tests/."""
    if MARKDOWN_PATTERN.search(path.as_posix()):
        return path.is_file()

    if not PYTHON_PATTERN.search(path.as_posix()):
        return False
    return bool(python.SRC_TEST_PATTERN.search(python.relative_path(path))) and path.is_file()


def file_violations(path: Path) -> tuple[Violation, ...]:
    """The punctuation violations for one file."""
    return punctuation_violations(read_unit(path))


def main() -> int:
    return run_check(in_scope, file_violations)


if __name__ == "__main__":
    sys.exit(main())
