"""Behavior tests for the Python hooks, runnable with the stdlib alone.

Run from the repository root: python3 -B .claude/hooks/tests/test_hooks.py
"""

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType

HOOKS = Path(__file__).resolve().parent.parent
sys.path.insert(0, HOOKS.as_posix())


def load(name: str) -> ModuleType:
    """The hook entry point loaded as a module, since its file name carries hyphens."""
    specification = importlib.util.spec_from_file_location(name.replace("-", "_"), HOOKS / f"{name}.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


layers = load("check-python-hexagonal-layers")
suppressions = load("check-python-suppressions")
punctuation = load("check-prose-punctuation")


class HexagonalLayersTest(unittest.TestCase):

    def test_domain_importing_a_third_party_package_is_reported(self) -> None:
        violations = layers.hexagonal_violations("src/application/domain/models/issue.py", "import github\n")
        self.assertEqual(1, len(violations))

    def test_domain_importing_the_standard_library_and_itself_conforms(self) -> None:
        source = "from dataclasses import dataclass\nfrom src.application.domain.exceptions.x import X\n"
        self.assertEqual((), layers.hexagonal_violations("src/application/domain/models/issue.py", source))

    def test_driver_importing_a_concrete_handler_is_reported(self) -> None:
        source = "from src.application.handlers.issues_assigning_handler import IssuesAssigningHandler\n"
        self.assertEqual(1, len(layers.hexagonal_violations("src/driver/console/assigners.py", source)))

    def test_driver_importing_an_inbound_port_conforms(self) -> None:
        source = "from src.application.ports.inbound.issues_assigning import IssuesAssigning\n"
        self.assertEqual((), layers.hexagonal_violations("src/driver/console/assigners.py", source))

    def test_handler_importing_a_driven_adapter_is_reported(self) -> None:
        source = "from src.driven.github.github_issues import GitHubIssues\n"
        self.assertEqual(1, len(layers.hexagonal_violations("src/application/handlers/handler.py", source)))

    def test_ports_importing_a_third_party_package_is_reported(self) -> None:
        source = "from github.Repository import Repository\n"
        self.assertEqual(1, len(layers.hexagonal_violations("src/application/ports/outbound/issues.py", source)))

    def test_driven_importing_a_third_party_package_conforms(self) -> None:
        source = "from github.Repository import Repository\nfrom src.application.ports.outbound.issues import Issues\n"
        self.assertEqual((), layers.hexagonal_violations("src/driven/github/github_issues.py", source))

    def test_relative_import_is_reported(self) -> None:
        self.assertEqual(1, len(layers.hexagonal_violations("src/driven/github/github_issues.py", "from . import x\n")))

    def test_composition_root_is_out_of_scope(self) -> None:
        source = "from src.driven.github.github_issues import GitHubIssues\n"
        self.assertEqual((), layers.hexagonal_violations("src/dependencies.py", source))


class SuppressionsTest(unittest.TestCase):

    def test_each_inline_suppression_is_reported(self) -> None:
        source = (
            "first = 1  # pylint: disable=invalid-name\n"
            "second = 2  # type: ignore[assignment]\n"
            "third = 3  # noqa: E501\n"
            "fourth = 4  # pragma: no cover\n"
        )
        self.assertEqual(4, len(suppressions.suppression_violations("src/module.py", source)))

    def test_suppression_text_inside_a_string_is_ignored(self) -> None:
        self.assertEqual((), suppressions.suppression_violations("src/module.py", "text = '# noqa'\n"))


class ProsePunctuationTest(unittest.TestCase):

    def test_semicolon_in_markdown_prose_is_reported(self) -> None:
        unit = punctuation.FileUnit(path="rule.md", text="One clause; another clause.\n")
        self.assertEqual(1, len(punctuation.markdown_violations(unit)))

    def test_semicolon_in_fenced_code_and_tables_is_exempt(self) -> None:
        unit = punctuation.FileUnit(path="rule.md", text="```\na; b\n```\n| a; b |\nUse `a; b` inline.\n")
        self.assertEqual((), punctuation.markdown_violations(unit))

    def test_em_dash_in_a_docstring_is_reported(self) -> None:
        unit = punctuation.FileUnit(path="src/module.py", text='"""Issues — open ones."""\n')
        self.assertEqual(1, len(punctuation.python_violations(unit)))

    def test_semicolon_in_python_code_is_not_prose(self) -> None:
        unit = punctuation.FileUnit(path="src/module.py", text="first = 1; second = 2\n")
        self.assertEqual((), punctuation.python_violations(unit))


if __name__ == "__main__":
    unittest.main()
