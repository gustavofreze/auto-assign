# Test Data Builder

Read this while constructing a test subject. None of it is a per-file invariant, so it is not path-injected. The
fixture ladder (inline, module-level helper, builder, pytest fixture for boundary doubles) and the builder home
(`tests/support/builders/`) live in `rules/python-testing.md` § Fixtures and builders. This file holds the construction
how-to, the builder skeleton, and the worked usages.

A type with a large construction signature cannot be built inline in every `# Given` without drowning the scenario in
noise. For that type, a **Test Data Builder** is the single sanctioned construction helper and the one place defaults
live in test code. One builder per type, consumed by every test module that constructs it.

## Builder versus inline construction

| Signature and reuse                                                | Strategy                                    | Example                                                                  |
|--------------------------------------------------------------------|---------------------------------------------|--------------------------------------------------------------------------|
| One or two trivial values                                          | Inline through the production constructor   | `Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())` |
| Reused across tests of the **same** module                         | Module-level helper function in that module | `def request_for(assignment_options: tuple[str, ...]) -> Request:`       |
| Past roughly five parameters, or reused across **several** modules | **Test Data Builder**                       | `AssignmentBuilder.new().build()`                                        |

- **Inline** when the constructor takes a small signature. Today `Issue` and `PullRequest` sit here: three and four
  keyword arguments, built inline in every test.
- **Module-level helper** when one instance repeats across the tests of a single module. It is a plain function with a
  full annotation and a business name (`request_for`, `assigners_over` in `tests/driver/console/test_assigners.py`),
  never `make_request` or `fixture_request`. It takes as parameters only the values the tests vary.
- **Builder** past roughly five construction parameters, or when the same type is built by several test modules.
  `Assignment` takes six and is built by both model test modules, so it has `AssignmentBuilder`.

A builder wrapping a constructor of five fields or fewer that only one module uses is surplus. Reach for inline
construction or a module-level helper first. A pytest fixture is never the answer for a domain value or a driver input
(`rules/python-testing.md`), fixtures are for boundary doubles that need setup.

## Builder shape

- **Placement.** `tests/support/builders/<type>_builder.py`, one public class per module, named `<Type>Builder`. The
  `Builder` suffix is legitimate only here (`rules/python-code-style.md` § Naming).
- **Class.** A `@final` `@dataclass(frozen=True, slots=True, kw_only=True)` whose fields mirror the constructor of the
  built type, ordered as `rules/python-code-style.md` § Ordering requires. Every code-style rule applies: full
  annotations, keyword arguments, no abbreviations, no `else`.
- **`new()`.** A `@staticmethod` returning a builder seeded with valid defaults that build a coherent instance with no
  further configuration. The return annotation names the class (`-> AssignmentBuilder`), never `Self`.
- **`with_<field>(...)`.** Returns a new builder through the constructor, naming every field, so the chain is
  immutable.
  A `with_*` method exists only when a test calls it. An unused one is dead code.
- **`build()`.** Calls the production constructor and returns its instance. It never catches the exception the
  constructor raises, so an invariant test sees it through `pytest.raises`.
- **State shortcuts.** For a model with transitions only. A `@staticmethod` (`assigned()`) returning a builder whose
  `build()` reaches the state through the **real** transition, never by passing a post-transition field straight to the
  constructor. The shortcut carries fixed internal inputs for the transition and exposes no `with_*` for them.

## Plain multi-field types have no state shortcuts

A value object such as `Assignment` (actor, assignees, eligibility, three flags) has many fields but no transitions.
Its builder exposes only `new()`, the `with_*` methods the tests call, and `build()`. State shortcuts exist solely for
models that transition.

## The AssignmentBuilder

`tests/support/builders/assignment_builder.py` holds the one builder of this repository. `test_issue.py` and
`test_pull_request.py` both build an `Assignment`, which takes six fields. Abridged to one `with_*` method (the module
holds one per field, each called by a test):

```python
from dataclasses import dataclass
from typing import final

from src.application.domain.models.commons.assignment import Assignment
from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AssignmentBuilder:
    actor: Login
    assignees: Logins
    eligibility: Eligibility
    assign_author: bool
    allow_self_assign: bool
    allow_no_assignees: bool

    @staticmethod
    def new() -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=Login(value='octocat'),
            assignees=Logins.from_raw(values=('alice', 'bob')),
            eligibility=Eligibility(skip_bots=False, skip_drafts=False),
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        )

    def with_assignees(self, assignees: Logins) -> AssignmentBuilder:
        return AssignmentBuilder(
            actor=self.actor,
            assignees=assignees,
            eligibility=self.eligibility,
            assign_author=self.assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )

    def build(self) -> Assignment:
        return Assignment(
            actor=self.actor,
            assignees=self.assignees,
            eligibility=self.eligibility,
            assign_author=self.assign_author,
            allow_self_assign=self.allow_self_assign,
            allow_no_assignees=self.allow_no_assignees
        )
```

Notes on the builder:

- Each step returns a new builder through the constructor, naming every field, never `dataclasses.replace`.
- The defaults live in `new()` and nowhere else. The dataclass fields declare none, so a builder can never be created
  half-configured.
- The fields are ordered by identifier length, mirroring `Assignment`.

## The form of a state shortcut

The current `Issue` takes three arguments and is built inline, so no `IssueBuilder` exists. When a model crosses the
threshold, a shortcut takes this form: the flag selects the target state and `build()` applies the real transition.

```python
    @staticmethod
    def assigned() -> IssueBuilder:
        builder = IssueBuilder.new()

        return IssueBuilder(number=builder.number, author=builder.author, is_assigned=True)

    def build(self) -> Issue:
        issue = Issue(number=self.number, author=self.author, assignees=Logins.empty())

        if not self.is_assigned:
            return issue

        return issue.assign(assignment=AssignmentBuilder.new().build())
```

The guard clause replaces an `else`. When the transition graph grows past two states, dispatch on a target enum
instead of stacking flags.

## Using the builder in a test

1. **Business name, never the helper's.** A named result is `assignment`, never `builder`. The step phrases describe
   the domain: `# When the pull request is assigned to alice while drafts are skipped`, never
   `# When an assignment builder with drafts skipped is applied`.
2. **One expression, ending in `build()`.** `mypy --strict` rejects rebinding a name from `AssignmentBuilder` to
   `Assignment`, so the chain stays one expression that ends in `build()` within the step where creation happens.
   Never a standalone `# When ... build()` that narrates the helper. Creation lands on:
    - `# When` when **creation is the action under test** (an invariant enforced in `__post_init__`, a normalization,
      a boundary acceptance or rejection).
    - `# Given` when creation is **setup** for a later action, and the `# When` is that action. A built value the
      action consumes once is inlined as its argument instead (`rules/python-testing.md` § Rules item 9).
3. **Values that matter are explicit.** A value the assertion reads appears as a `with_*` call in the chain and in the
   step phrase. Values irrelevant to the test stay in the `new()` defaults. Never spell them out, and never let an
   assertion depend on a default it does not show.
4. **State shortcuts only when the path is irrelevant.** If the assertion reads only the direct effect of the `# When`,
   `IssueBuilder.assigned().build()` is fine. If it depends on a value an intermediate transition injects, spell the
   transition out as an `# And` step on the real model instead of hiding it in the shortcut.

## Cover actions and invariants, not accessors

A test exercises a **domain action**: a constructor that enforces an invariant or a transition that returns a new
instance. It never asserts that a constructor stored what it was handed. "Construct with X, then the attribute is X"
exercises the dataclass, not behavior, and is removed. Cover an invariant by repeating the **same action with different
values**, one accepted and one rejected, as one parameterized test or as a pair of tests when the outcomes differ in
kind (a new instance against a raised exception).

## Grouping assertions

One logical concept per `# Then` (`rules/python-testing.md` § Rules item 5). When the verification spans distinct
concepts, add an `# And` block after a blank line. Never stack every assertion under one comment.

## Usage 1, creation as the action under test

When a type enforces an invariant at construction, `build()` sits inside `pytest.raises` on the `# When`. No builder
target in this repository validates at construction today: `Assignment` has no `__post_init__`, and
`AssigneesRequired` is raised later, by `granted_assignees`, when a model is assigned. The fragment shows the shape
for the day a built type gains a `__post_init__` invariant:

```python
    # Then the assignment is refused because it names no assignee
    with pytest.raises(AssigneesRequired):
        # When an assignment is built without assignees while an empty assignment is denied
        AssignmentBuilder.new().with_assignees(assignees=Logins.empty()).build()
```

The acceptance twin repeats the same chain with an assignee and asserts the instance the chain returns.

## Usage 2, creation as setup for the action

The builder fixes only the values the outcome depends on, and the chain is the argument of the `# When`, because the
assignment is consumed once. The actor and the self-assignment flags stay in the defaults because no assertion reads
them.

```python
def test_assign_when_a_draft_is_assigned_and_drafts_are_skipped_then_the_pull_request_stays_unchanged() -> None:
    # Given a draft pull request without assignees
    pull_request = PullRequest(number=7, draft=True, author=Login(value='carol'), assignees=Logins.empty())

    # When the pull request is assigned to alice while drafts are skipped
    assigned_pull_request = pull_request.assign(
        assignment=AssignmentBuilder.new()
        .with_assignees(assignees=Logins.from_raw(values=('alice',)))
        .with_eligibility(eligibility=Eligibility(skip_bots=False, skip_drafts=True))
        .build()
    )

    # Then the pull request stays without assignees
    assert assigned_pull_request == PullRequest(
        number=7,
        draft=True,
        author=Login(value='carol'),
        assignees=Logins.empty()
    )
```

## Cross-references

- `rules/python-testing.md`: the fixture ladder, the builder home, one concept per `# Then`, and inlining a value used
  once.
- `rules/python-code-style.md`: frozen dataclasses, `@final`, static factories, ordering, and keyword arguments.
- `rules/python-domain.md`: invariants in `__post_init__` and transitions through the class constructor.
