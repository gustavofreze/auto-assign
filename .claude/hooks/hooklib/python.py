"""Python language module: scope patterns, parsing, import scanning, and comment and
docstring extraction.

This module is the language seam. Entry points take everything Python-specific from here.
Parsing failures return empty results, because a file mid-edit may not parse yet and the
linter, not a hook, owns syntax errors.
"""

import ast
import io
import re
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from hooklib.core import project_root

# In-scope patterns for Python sources, relative to the project root.
SRC_PATTERN: Final = re.compile(r"^src/.+\.py$")
SRC_TEST_PATTERN: Final = re.compile(r"^(src|tests)/.+\.py$")

# Top-level names of the standard library, the only outside modules the core may import.
STANDARD_LIBRARY: Final = frozenset(sys.stdlib_module_names) | {"__future__"}


@dataclass(frozen=True)
class Import:
    """One imported module and the line that imports it."""

    line: int
    module: str
    relative: bool


@dataclass(frozen=True)
class Prose:
    """One comment or docstring and the line it starts on."""

    line: int
    text: str


def relative_path(path: Path) -> str:
    """The path relative to the project root in POSIX form, or the path itself when outside it."""
    resolved = path.resolve()
    root = project_root().resolve()

    if resolved.is_relative_to(root):
        return resolved.relative_to(root).as_posix()
    return path.as_posix()


def parse(text: str) -> ast.Module | None:
    """The module tree, or None when the source does not parse."""
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def imports(text: str) -> tuple[Import, ...]:
    """Every module imported anywhere in the source, `from` and plain imports alike."""
    tree = parse(text)

    if tree is None:
        return ()

    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(Import(line=node.lineno, module=alias.name, relative=False) for alias in node.names)

        if isinstance(node, ast.ImportFrom):
            found.append(Import(line=node.lineno, module=node.module or "", relative=node.level > 0))
    return tuple(found)


def is_standard_library(module: str) -> bool:
    """Whether the module belongs to the standard library."""
    return module.split(".")[0] in STANDARD_LIBRARY


def comments(text: str) -> tuple[Prose, ...]:
    """Every `#` comment in the source, with its line."""
    found = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                found.append(Prose(line=token.start[0], text=token.string))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return tuple(found)
    return tuple(found)


def docstrings(text: str) -> tuple[Prose, ...]:
    """Every module, class, and function docstring in the source, with its first line."""
    tree = parse(text)

    if tree is None:
        return ()

    holders = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, holders) or not node.body:
            continue

        first = node.body[0]

        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            found.append(Prose(line=first.lineno, text=first.value.value))
    return tuple(found)
