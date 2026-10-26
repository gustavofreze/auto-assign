#!/usr/bin/env python3
"""Inline analyzer suppression check for Python sources under src/ and tests/.

`# pylint: disable`, `# type: ignore`, `# noqa`, and `# pragma: no cover` are prohibited
in every Python file. The suppression channels are `.pylintrc`, the mypy sections of
`pyproject.toml`, and `.coveragerc`, see rules/python-code-style.md § Analyzer suppressions.
"""

import re
import sys
from pathlib import Path
from typing import Final

from hooklib import python
from hooklib.core import Violation, read_unit, run_check

SUPPRESSION: Final = re.compile(
    r"#\s*(pylint:\s*disable|type:\s*ignore|noqa|pragma:\s*no\s*cover)",
    re.IGNORECASE,
)


def suppression_violations(path: str, text: str) -> tuple[Violation, ...]:
    """The inline suppressions found in one module's comments."""
    return tuple(
        Violation(
            line=comment.line,
            path=path,
            message=(
                f"inline suppression `{comment.text.strip()}`, fix the code or scope the concession in "
                f".pylintrc, pyproject.toml [tool.mypy], or .coveragerc"
            ),
        )
        for comment in python.comments(text)
        if SUPPRESSION.search(comment.text)
    )


def in_scope(path: Path) -> bool:
    """Whether the path is a Python module under src/ or tests/."""
    return bool(python.SRC_TEST_PATTERN.search(python.relative_path(path))) and path.is_file()


def file_violations(path: Path) -> tuple[Violation, ...]:
    """The suppression violations for one module."""
    unit = read_unit(path)
    return suppression_violations(python.relative_path(path), unit.text)


def main() -> int:
    return run_check(in_scope, file_violations)


if __name__ == "__main__":
    sys.exit(main())
