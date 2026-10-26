---
description: Pre-output checklist, typing, immutability, naming, docstrings, exceptions, imports, and formatting rules for all Python files.
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Code style

Semantic rules for every Python file. Run `make review` after every change. **Target Python version: the version
declared in `pyproject.toml` (`[tool.poetry.dependencies] python`).** Use the cleanest syntax that floor natively
supports over a more verbose legacy form. Refer to `rules/python-domain.md` for value objects, enums, and domain
exceptions.

## Pre-output checklist

Verify every item before producing any Python code. If any item fails, revise before outputting.

1. Every parameter, return value, and attribute is explicitly typed, `-> None` included. `mypy --strict` reports
   clean. See § Typing.
2. Builtin generics and union syntax only: `list[str]`, `dict[str, int]`, `X | None`. Never `typing.List`, `Dict`,
   `Optional`, or `Union`. No `Any` and no bare `object` where a concrete or domain type exists. See § Typing.
3. Concrete classes carry `@final` and never inherit from each other. Inheritance is reserved for implementing an
   `ABC` port, for extending an exception base, and for the empty `@final` commands over their shared command base
   (`AssignmentCommand`, `rules/python-architecture.md` § Commands and handlers). Use composition, and no private
   methods under `src/`: a helper step is its own collaborator class. See § Classes.
4. Domain models, value objects, commands, and DTOs are `@dataclass(frozen=True, slots=True, kw_only=True)` with no
   hand-written `__init__`. Mutation returns a new instance through the class constructor, never
   `dataclasses.replace`. Collections they hold are `tuple` or `frozenset`, never `list`, `set`, or `dict`. See §
   Immutability.
5. No `else` or `elif` exists anywhere. Use early returns, a dispatch `dict`, polymorphism, or `match`. See § Control
   flow.
6. No abbreviations and no single-letter identifiers, loop variables and comprehensions included (`index`, not `i`,
   `assignee`, not `a`). `_` is allowed only for a value deliberately discarded. See § Naming.
7. No generic identifiers: `data` becomes `issue_payload`, `value` becomes `total_amount`, `item` becomes
   `line_item`, `info` becomes `client_details`, `result` becomes `assignment_outcome`. See § Naming.
8. Own-code call sites pass arguments by keyword. Builtins, the standard library, and assertions stay positional. No
   argument equals the parameter's default. See § Keyword arguments.
9. The domain layer declares no default parameter values. Elsewhere a default is a neutral value most callers would
   repeat verbatim, never a business choice (`allow_self_assign: bool = True` is forbidden). See § Default values.
10. Parameters, dataclass fields, and keyword arguments order by identifier length ascending, alphabetical tie-break,
    semantic pairs (`start`/`end`, `source`/`target`) in natural order. See § Ordering.
11. Docstrings live on ports only (the `ABC` and each abstract method). Concrete classes, functions, and their methods
    carry none. See § Docstrings.
12. No `except` is empty, bare (`except:`), or swallows silently. `except Exception` appears only at the outermost
    boundary (`src/main.py` and the console driver). A translated exception is chained with `raise ... from`. See §
    Exceptions.
13. Imports are absolute (`from src.application...`), one module per `from` line, never relative, never `*`, never
    inside a function. See § Imports.
14. No inline linter or type-checker suppression: `# pylint: disable`, `# type: ignore`, `# noqa`, and
    `# pragma: no cover` are prohibited. See § Analyzer suppressions.
15. No dead code: an unreferenced class, function, constant, attribute, parameter, or import is removed. No public
    name exists solely to serve tests.
16. No justification comments (`# NOTE:`, `# REASON:`). Code speaks for itself. `# TODO: <reason>` marks deferred or
    uncertain work, never a silent gap.
17. No O(N²) or worse where a `set` or `dict` lookup gives O(N). No logic duplicated across two or more places, and no
    abstraction without real duplication or isolation need.
18. All identifiers, comments, docstrings, and messages use American English.
19. Formatting holds: 120-column lines, one parameter per line only when the single line overflows, no trailing comma
    after the last element of a multi-line list, and method bodies read as blank-line-separated paragraphs. See §
    Formatting.
20. `make review` and `make test` were run after the change and report clean.

## Typing

1. Every function and method signature is fully annotated, including `-> None` and `self`-less static factories.
2. Annotations name the class directly. A `@final` class names itself in the return type of its own factory
   (`def success() -> Result`), never `Self`.
3. Use builtin generics and `|` unions. `collections.abc` supplies `Iterable`, `Sequence`, `Mapping`, and `Callable`
   when a parameter accepts any such shape.
4. `Any` is prohibited. A third-party value with no type stub is narrowed at the driven boundary into a domain type,
   and the gap is declared once in `pyproject.toml` (`[[tool.mypy.overrides]]`), never at the call site.
5. Raw strings and integers that carry business meaning are promoted to a value object or enum at the boundary that
   receives them. Primitive obsession inside the hexagon is a defect.

## Classes

1. Every concrete class is decorated with `typing.final`. Inheritance between concrete classes is prohibited. The one
   carve-out is a command base (`AssignmentCommand`): it stays non-final so each use-case command can be an empty
   `@final` subclass that adds no field and no behavior.
2. A class extends only an `ABC` port it implements, an exception base, or, for a command, its command base. Never
   extend for reuse.
3. Ports are `abc.ABC` subclasses with `@abstractmethod` methods. Implementation is explicit (`class
   GitHubIssues(Issues)`), so the dependency is visible in the source.
4. Instance state of a service class (handler, adapter, driver) is assigned once in `__init__` to single-underscore
   attributes (`self._issues`). Name mangling (`self.__issues`) is not used.
5. Named alternative constructors are `@staticmethod` factories on the class (`Result.success()`), returning a new
   instance of that class.
6. Production classes under `src/` declare no private methods (`def _records(self)`). A step a public method needs is
   a responsibility of its own: give it a `@final` collaborator class, injected through the constructor
   (`GitHubIssueRecords` selects the records in scope for `GitHubIssues`), or one implementation per variant behind
   an `ABC` (`IssuesAssigner`, `PullRequestsAssigner` behind `Assigner`). Private attributes holding state stay.

## Immutability

1. Value types use `@dataclass(frozen=True, slots=True, kw_only=True)`. Never pair `@dataclass` with a hand-written
   `__init__`: the decorator then generates nothing useful and the class is silently mutable.
2. Invariants are enforced in `__post_init__`, which raises a domain exception on invalid input.
3. Held collections are `tuple[...]` or `frozenset[...]`. A `list` handed in at a boundary is converted once, at
   construction.
4. A transition returns a new instance through the class constructor, naming every field
   (`Issue(number=self.number, author=self.author, assignees=assignees)`). `dataclasses.replace` is not used: its
   declared return type is `DataclassInstance`, so Sonar and the IDE lose the concrete type at every call. Nothing is
   mutated in place.

## Control flow

1. No `else`, no `elif`, including `for ... else` and `try ... else`.
2. Guard clauses return or raise early, so the happy path is never nested.
3. A branch per variant is a dispatch `dict`, a `match` statement, or polymorphism behind a port.
4. At most four non-guard `return` statements per function. Past that, rewrite with dispatch to a single return.
5. Length is a readability signal, not a metric. Past roughly fifty logical lines, review the cause of the length and
   move the rule to its owner, never trim to a number.

## Naming

1. Modules and packages are `snake_case` (`issues_assigning_handler.py`). Classes are `PascalCase`. Functions, methods,
   attributes, and variables are `snake_case`. Constants and enum members are `SCREAMING_SNAKE_CASE`. One public
   class per module, and the module is named after it.
2. Names describe **what** in business terms, not **how** technically: `monthly_revenue`, not `calculated_value`.
3. Generic technical verbs (`process`, `handle`, `execute`, `perform`, `manage`, `do`, `run`, `apply`, `check`,
   `validate`) are prohibited in `src/application/domain/` and avoided elsewhere. Exception: the inbound port method
   `handle` is fixed by convention.
4. Booleans and `bool`-returning methods read as predicates: `is_`, `has_`, `can_`, `was_`, `should_`, or a
   relational third-person verb taking the operand (`belongs_to`, `contains`, `equals`, `matches`).
5. Collections are plural (`issues`, `assignees`).
6. A design pattern is a shape, never a name. Pattern suffixes (`...Strategy`, `...Factory`, `...Decorator`,
   `...Visitor`, `...Manager`, `...Helper`, `...Util`) are prohibited. Adapter-kind suffixes (`Repository`,
   `Gateway`, `Client`, `Publisher`) and `Settings` are legitimate. `Builder` is legitimate only on a test data
   builder under `tests/support/builders/`.
7. Local exception names say what failed: `except GithubException as lookup_failure`. `e`, `ex`, and `err` are
   prohibited.

## Keyword arguments

Pass arguments by keyword at every call into own code and into third-party library code
(`Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())`). Keep positional calls for builtins, the
standard library, `pytest` assertions, and variadic spread (`*assignees`). Never pass an argument equal to the
parameter's default, omit it.

## Default values

The domain layer declares no default parameter or field values: every input is required, and each distinct input
shape is a named factory. Elsewhere a default is acceptable only as a neutral identifiable value most callers repeat
verbatim. Defaults that skip a field or express a business choice are forbidden in every layer, tests included. A
mutable default (`[]`, `{}`) is always a defect.

## Ordering

Function parameters, dataclass fields, and keyword arguments at call sites order by identifier length ascending,
alphabetical tie-break, with semantic pairs kept in natural order. Dataclass fields group first by meaning (identity,
then core state, then metadata), and order by length within each group.

## Docstrings

1. Required on every port (`ABC`) and every abstract method. Prohibited on concrete classes, functions, and methods.
   The name and signature must speak for themselves.
2. The first line is a domain-terms summary ending with a period. A port summary is nominal (`Issues awaiting an
   assignee.`). A method summary is third-person present (`Assigns the issue to its assignees.`), never imperative,
   past, or passive.
3. Prohibited openers: `Interface for`, `Contract for`, `Wrapper for`, `Represents`, `Used to`, `Helper for`,
   `Provides`, `Defines`, `Handles`, `Processes`. Never name the Python construct, the storage, or the design role
   (`port`, `adapter`, `use case`, `command`, `payload`).
4. Fields use reST: `:param name: The {noun phrase}.`, `:returns: The {noun phrase}.`, `:raises Exception: When
   {domain condition}.`. Every field ends with a period.

## Exceptions

1. Errors are raised, never returned as sentinels (`None`, `[]`, `False`) to signal a failure.
2. A `catch` translates, re-raises, or returns a value that expresses the recovery. An empty body or `pass` is
   prohibited.
3. Translation chains the cause with `from`:
   `raise GitHubRequestFailed(status=lookup_failure.status, operation=...) from lookup_failure`.
4. `except Exception` is allowed only where the process turns a failure into an exit code: `src/main.py` and the
   console driver.
5. Domain exception shape and placement are owned by `rules/python-domain.md` and `rules/python-architecture.md`.

## Imports

1. Absolute imports rooted at `src` (or `tests` in test code). No relative imports, no wildcard imports.
2. Order: standard library, third party, own code, each group separated by one blank line.
3. Imports sit at module top. An import inside a function is prohibited.
4. Never alias an import to dodge a name clash (`import Adapter as IssuesAdapter`). A clash means two classes share a
   generic name: rename the classes.

## Analyzer suppressions

The only places a finding is suppressed are the tool configurations: `.pylintrc` for pylint, `[tool.mypy]` and
`[[tool.mypy.overrides]]` in `pyproject.toml` for mypy, and `.coveragerc` for coverage. Inline directives are
prohibited in every Python file: `# pylint: disable`, `# pylint: disable-next`, `# type: ignore`, `# noqa`,
`# pragma: no cover`.

An inline directive silences one finding at one line and then travels with that line. It survives the rename that
moved the code and the refactor that made it unnecessary, and nothing reports it as obsolete. A configuration entry is
scoped by module and checker, carries the comment that justifies it, and keeps every concession in one reviewable
place. Fix the code first. A finding about the project's own code is a defect in that code, and widening an exclusion
to hide it is a second defect.

## Comparisons

1. `None` checks use `is None` and `is not None`, never `==`.
2. Truthiness is used only on collections and `bool` values. A string is compared with `== ''`.
3. Two value objects of the same type compare through `==` (dataclass value equality) or a predicate the type
   exposes, never by unwrapping fields at the call site.

## Local variables and call nesting

In `src/`, prefer a named intermediate variable over nesting one call's result inside another: build the command into
`command` before `handler.handle(command=command)`. A fluent chain on one receiver stays a chain. Tests do the
opposite: a value consumed once is inlined (owned by `rules/python-testing.md`).

## Formatting

1. Lines stay within 120 columns.
2. A signature or call stays on one line when it fits. When it overflows, put one parameter per line with a hanging
   indent, and the closing parenthesis on its own line.
3. No trailing comma after the last element of a multi-line parameter list, argument list, or literal.
4. Strings use single quotes, f-strings for interpolation. Never `%` formatting or `str.format`.
5. A function body reads as short paragraphs, one per step, separated by a single blank line: guards, the work, then
   the trailing `return` set off by a blank line. A blank line never splits a tight pair (a value built and
   immediately handed to the call it serves). Do not pad a one-statement body.

## American English

All identifiers, enum values, comments, docstrings, and messages use American English spelling: `canceled`,
`organization`, `initialize`, `behavior`, `modeling`, `labeled`, `fulfill`, `color`.
