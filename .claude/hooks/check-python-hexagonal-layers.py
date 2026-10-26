#!/usr/bin/env python3
"""Hexagonal layer check for the Python hexagon under src/.

Dependencies point inward only. The domain imports the standard library and itself, the
rest of the application core imports no third party and no outer layer, and adapters never
reach a concrete handler. The composition root (src/main.py, src/dependencies.py) wires every
layer and is out of scope, and so are tests.
"""

import re
import sys
from pathlib import Path
from typing import Final

from hooklib import python
from hooklib.core import Violation, read_unit, run_check

# Layer detection by path, most specific first, because domain nests inside application.
LAYER_PATTERNS: Final = (
    ("domain", re.compile(r"^src/application/domain/")),
    ("commands", re.compile(r"^src/application/commands/")),
    ("ports", re.compile(r"^src/application/ports/")),
    ("handlers", re.compile(r"^src/application/handlers/")),
    ("application", re.compile(r"^src/application/")),
    ("driver", re.compile(r"^src/driver/")),
    ("driven", re.compile(r"^src/driven/")),
)

# Own-code prefixes each layer must never import.
FORBIDDEN_OWN: Final = {
    "commands": ("src.application.ports", "src.application.handlers", "src.driver", "src.driven", "src.dependencies"),
    "ports": ("src.application.handlers", "src.driver", "src.driven", "src.dependencies"),
    "handlers": ("src.application.handlers", "src.driver", "src.driven", "src.dependencies"),
    "application": ("src.driver", "src.driven", "src.dependencies"),
    "driver": ("src.application.handlers", "src.driven", "src.dependencies"),
    "driven": ("src.application.handlers", "src.application.commands", "src.driver", "src.dependencies"),
}

# Layers of the application core, which import no third-party package.
CORE_LAYERS: Final = frozenset({"domain", "commands", "ports", "handlers", "application"})


def layer_of(path: str) -> str:
    """The hexagon layer of the module, or an empty string for the root or an out-of-layer module."""
    for name, pattern in LAYER_PATTERNS:
        if pattern.search(path):
            return name
    return ""


def is_within(module: str, prefix: str) -> bool:
    """Whether the module is the prefix itself or nested under it."""
    return module == prefix or module.startswith(f"{prefix}.")


def domain_reason(module: str) -> str:
    """The reason a domain import is forbidden, empty when allowed."""
    if is_within(module, "src.application.domain") or python.is_standard_library(module):
        return ""
    return (
        f"domain imports `{module}`, the domain depends only on the standard library and "
        f"src.application.domain, see rules/python-domain.md § Import whitelist"
    )


def layer_reason(layer: str, module: str) -> str:
    """The reason an import is forbidden from a non-domain layer, empty when allowed."""
    own = is_within(module, "src")

    if layer in CORE_LAYERS and not own and not python.is_standard_library(module):
        return (
            f"{layer} imports the third-party `{module}`, the application core stays free of "
            f"frameworks and SDKs, move the dependency behind an outbound port in src/driven"
        )

    forbidden = next((prefix for prefix in FORBIDDEN_OWN.get(layer, ()) if is_within(module, prefix)), "")

    if not forbidden:
        return ""
    return (
        f"{layer} imports `{module}`, dependencies point inward and adapters depend on ports, "
        f"never on `{forbidden}`, see rules/python-architecture.md § Layer contract"
    )


def reason(layer: str, imported: python.Import) -> str:
    """The reason one import breaks the layer contract, empty when it conforms."""
    if imported.relative:
        return "relative import, imports are absolute and rooted at `src`, see rules/python-code-style.md § Imports"

    if layer == "domain":
        return domain_reason(imported.module)
    return layer_reason(layer, imported.module)


def hexagonal_violations(path: str, text: str) -> tuple[Violation, ...]:
    """The layer-coupling violations for one module."""
    layer = layer_of(path)

    if not layer:
        return ()

    violations = []
    for imported in python.imports(text):
        message = reason(layer, imported)

        if message:
            violations.append(Violation(line=imported.line, path=path, message=message))
    return tuple(violations)


def in_scope(path: Path) -> bool:
    """Whether the path is a Python module under src/."""
    return bool(python.SRC_PATTERN.search(python.relative_path(path))) and path.is_file()


def file_violations(path: Path) -> tuple[Violation, ...]:
    """The hexagonal violations for one module."""
    unit = read_unit(path)
    return hexagonal_violations(python.relative_path(path), unit.text)


def main() -> int:
    return run_check(in_scope, file_violations)


if __name__ == "__main__":
    sys.exit(main())
