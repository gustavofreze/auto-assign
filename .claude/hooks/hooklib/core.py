"""Language-agnostic scaffolding shared by every hook entry point.

Covers the PostToolUse contract: read the edited path from argv or the stdin payload,
collect violations over in-scope files, and report through the exit-code protocol
(exit 0 silent success, exit 2 with stderr fed back to Claude).
"""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final, Iterable

MAX_ERRORS_REPORTED: Final = 30


@dataclass(frozen=True)
class Violation:
    """One violation at a source position."""

    line: int
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


@dataclass(frozen=True)
class FileUnit:
    """One file under analysis: its path and raw text."""

    path: str
    text: str


def read_unit(path: Path) -> FileUnit:
    """The FileUnit for one path, with undecodable bytes replaced."""
    return FileUnit(
        path=path.as_posix(),
        text=path.read_text(errors="replace", encoding="utf-8"),
    )


def project_root() -> Path:
    """The repository root, from CLAUDE_PROJECT_DIR when set, else the working directory."""
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(root) if root else Path.cwd()


def stdin_file_path() -> Path | None:
    """The edited file path from the hook's stdin payload, or None when unavailable."""
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return None

    file_path = (payload.get("tool_input") or {}).get("file_path")

    if isinstance(file_path, str):
        return Path(file_path)
    return None


def requested_paths() -> list[Path]:
    """The paths to verify, from argv or from the hook's stdin payload."""
    if len(sys.argv) > 1:
        return [Path(argument) for argument in sys.argv[1:]]

    path = stdin_file_path()
    return [] if path is None else [path]


def report(violations: list[Violation]) -> int:
    """Print the violations to stderr under the error cap, exit code 2 when any exist."""
    if not violations:
        return 0

    for violation in violations[:MAX_ERRORS_REPORTED]:
        print(violation, file=sys.stderr)
    overflow = len(violations) - MAX_ERRORS_REPORTED

    if overflow > 0:
        print(f"... and {overflow} more violations", file=sys.stderr)
    return 2


def run_check(
    in_scope: Callable[[Path], bool],
    file_violations: Callable[[Path], Iterable[Violation]],
) -> int:
    """The shared entry-point loop: check every in-scope requested path, then report."""
    violations = [
        violation
        for path in requested_paths()
        if in_scope(path)
        for violation in file_violations(path)
    ]
    return report(violations)
