---
description: Domain layer building blocks for Python, the folder structure, ubiquitous-language naming, models and value objects as frozen dataclasses, enums, domain exceptions, and the domain import whitelist.
paths:
  - "src/application/domain/**/*.py"
---

# Domain layer

The domain is entirely isolated from infrastructure, frameworks, and libraries. Refer to `rules/python-code-style.md`
for the checklist applied to all Python code.

## Pre-output checklist

1. The module imports only the standard library and `src.application.domain.*`. Never PyGithub, never
   `dependency_injector`, never `os.environ`, never `src.driver`, `src.driven`, or `src.dependencies`. See § Import
   whitelist.
2. Every model and value object is a `@final` `@dataclass(frozen=True, slots=True, kw_only=True)` with invariants in
   `__post_init__`. See § Models and value objects.
3. Every name comes from the business vocabulary. No `Manager`, `Helper`, `Processor`, `Handler`, `Data`, `Info`,
   `Utils`, `Service`, `Item`, `Record`, or `Entity` as a prefix or suffix. See § Nomenclature.
4. A behavior that decides on a model's state is a method on that model, not a function that reads its fields from
   outside (Tell, Don't Ask).
5. A domain exception signals one invariant violation, extends the domain base exception, and carries no exit code,
   log format, or transport detail. See § Domain exceptions.

## Folder structure

```
src/application/domain/
├── models/
│   ├── commons/                # Shared value objects reused by more than one model
│   ├── <model>.py              # Model or aggregate
│   ├── <model>_status.py       # Status enum
│   └── <model>_kind.py         # Kind enum
└── exceptions/
    ├── domain_exception.py     # The base every domain exception extends
    └── <violation>.py          # One module per domain exception
```

Never use `domain/entities/`, `domain/value_objects/`, or `domain/enums/` as folder names.

## Import whitelist

The domain imports the standard library (`dataclasses`, `enum`, `typing`, `collections.abc`, `abc`, `datetime`,
`decimal`, `uuid`, `re`) and its own modules under `src.application.domain`. Nothing else. A need for anything outside
the whitelist means the code is not domain: split the rule from the I/O and push the I/O behind an outbound port.

## Nomenclature (ubiquitous language)

1. Every class, attribute, method, and exception name is extracted from the business vocabulary (issue, pull request,
   assignee, actor, assignment). No exceptions.
2. Name classes after what they represent in the business (`Issue`, `PullRequest`, `Assignee`), not after what they
   do technically.
3. Name methods after business operations (`assign`, `unassign`), not `process`, `handle`, or `execute`.
4. When a term does not exist in the business vocabulary, the model is wrong. Revise it.

## Models and value objects

1. Immutable: `frozen=True`, `slots=True`, `kw_only=True`. No setters, no in-place mutation.
2. Invariants are validated in `__post_init__`, raising a domain exception.
3. Equality is by value (the dataclass `__eq__`). A model with identity compares through its typed identifier.
4. Collections are `tuple` or `frozenset`.
5. A transition returns a new instance through the class constructor (`Issue(number=self.number,
   author=self.author, assignees=assignees)`), never `dataclasses.replace`. A transition the rules decline returns
   `self` unchanged (`Issue.assign` when `assignment.excludes(author=..., draft=...)`).
6. A pure method that encodes an invariant or a derived calculation of the type lives on the type. A rule that two
   models share lives in a value object under `models/commons/`, never duplicated across both.

## Enums

1. Implemented with `enum.StrEnum` for string values and `enum.IntEnum` for integer values, members in
   `SCREAMING_SNAKE_CASE`.
2. Parsing a raw value is a `@staticmethod` on the enum (`IssueState.from_raw(raw=...)`) that raises a domain
   exception when the value is not a member. An enum that models action configuration rather than business state (the
   assignment options) is not domain: it lives in the driver and raises a driver exception
   (`rules/python-architecture.md` § Error placement).
3. Behavior that varies per member is a method on the enum, never an `if` chain at the call site.
4. Placed in `domain/models/`.

## Domain exceptions

1. Every domain exception extends `DomainException`, which extends `Exception`.
2. One exception per invariant, named by what failed. The form is not a style choice, it tells the reader the kind
   of failure:

   | What failed                                          | Form                    | Examples                      |
   |:-----------------------------------------------------|:------------------------|:------------------------------|
   | A string fails promotion to a value object on format | `<Thing>FormatNotValid` | `LoginFormatNotValid`         |
   | A value is empty where the type forbids it           | `<Thing>CannotBeEmpty`  | `LoginCannotBeEmpty`          |
   | A required value is absent                           | `<Thing>Required`       | `AssigneesRequired`           |
   | A raw value fails promotion to a closed-set enum     | `Unsupported<Thing>`    | `UnsupportedIssueState`       |
   | A domain invariant breaks (transition, range)        | `Invalid<Thing>`        | `InvalidAssignmentTransition` |
   | A business rule refuses a well-formed operation      | `<Thing><Condition>`    | `SelfAssignmentNotAllowed`    |

3. Pure: the message is a plain English sentence describing the violated invariant. No exit code, no log level, no
   ANSI or Markdown formatting. Presentation happens at the driver boundary.
4. Context is carried as typed domain values. Carve-out: an exception raised when a raw value cannot be promoted to a
   value object or enum may carry that raw value as a primitive, because no value object exists yet to hold it.
5. Not-found, conflict, and infrastructure failures are never domain exceptions (`rules/python-architecture.md` §
   Error placement).

## Principles

- **Immutability**: every domain type is immutable.
- **SOLID**: applies throughout. The precedence when principles collide is owned by
  `rules/python-design-principles.md`.
