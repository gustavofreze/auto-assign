# Design principles, in depth

This file is the deep reference behind the tables in `SKILL.md`. Each principle carries the rule, the
smell that signals it, a fuller good-versus-bad example in a neutral domain (Order, Customer, Account,
Money, Email, Report, Shape) or in auto-assign terms, and the trade-off that bounds it. SOLID is one
group among the principles, not the whole story. The Python shape these principles take in this
repository is enforced by `rules/python-code-style.md`, `rules/python-domain.md`, and
`rules/python-architecture.md`. Read the rule before you write.

The examples follow those rules: full annotations, `@final` concrete classes, frozen dataclasses,
keyword arguments, no `else` or `elif`, and docstrings on ABC ports only. Imports are omitted, and a
`...` body stands for code the example does not need. The comments are there to teach, production
code carries none of them.

## Contents

- SOLID
- Separation of Concerns
- High Cohesion
- Loose Coupling
- DRY
- KISS
- YAGNI
- Tell, Don't Ask
- Law of Demeter
- Composition over inheritance

## SOLID

The five class-level heuristics. Where each lands in ports and adapters is summarized in `SKILL.md`.

### Single Responsibility

A class should have one reason to change. Framed by the actor, it answers to one stakeholder. A report
class that holds the content rule, renders HTML, and writes a file answers to three: the analyst who
owns the numbers, the designer who owns the layout, and the operator who owns storage. A change for any
one of them risks the other two.

The test is not size. A long class with one cohesive job is fine. The test is the axis of change. When
two parts of a class vary for different reasons and on different days, they belong apart.

```python
# Bad: one class, three actors, three reasons to change.
@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Report:
    lines: tuple[ReportLine, ...]

    def total(self) -> Money:
        ...  # the analyst's rule

    def as_html(self) -> str:
        ...  # the designer's layout

    def save_to(self, path: Path) -> None:
        ...  # the operator's storage


# Good: the rule keeps its home, the other concerns move to their own seams.
@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Report:
    lines: tuple[ReportLine, ...]

    def total(self) -> Money:
        ...  # the one responsibility


@final
class ReportHTMLView:

    def render(self, report: Report) -> str:
        ...  # layout only


class Reports(ABC):
    """Computed reports kept for later reading."""

    @abstractmethod
    def save(self, report: Report) -> None:
        """Keeps the report for later reading.

        :param report: The computed report.
        :raises ReportNotSaved: When the report cannot be kept.
        """
```

In this repository the console driver is the presentation seam. A handler never formats a log line
or picks an exit code, and a model never knows either exists.

Trade-off: split too eagerly, and you scatter one cohesive idea across many tiny classes, which reads
worse than the class you feared. Split on a demonstrated second reason to change, not on a guess that
one will appear.

### Open-Closed

A unit should be open to extension and closed to modification. You add behavior without editing code
that already works. In Python the mechanism is a small ABC with a new implementing class, so a new
variant is a new class that declares the ABC it implements, and the stable code does not learn about
it.

The smell is a conditional over a variant that lives outside the type owning that variant and grows an
arm per kind, whether written as a `match`, an `isinstance` chain, or a dispatch `dict` keyed on a
type. Inside the owner (an enum's `from_raw` factory, a behavior method on the enum that varies per
member, a dispatch `dict` the enum keeps to itself) a `match` is canonical, not a violation.

```python
# Bad: a central match edited for every new shape.
@final
class AreaCalculator:

    def area(self, shape: Circle | Square) -> float:
        match shape:
            case Circle(radius=radius):
                return math.pi * radius * radius
            case Square(side=side):
                return side * side
            # a Triangle means editing here, again


# Good: each shape owns its area. A Triangle is a new class and edits nothing.
class Shape(ABC):
    """Closed plane figure with a known area."""

    @abstractmethod
    def area(self) -> float:
        """Returns the area of the figure.

        :returns: The area in square units.
        """


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Circle(Shape):
    radius: float

    def area(self) -> float:
        return math.pi * self.radius * self.radius


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Square(Shape):
    side: float

    def area(self) -> float:
        return self.side * self.side
```

Trade-off: an abstraction added before the second variant is speculative generality. Wait for the
second real kind, then close the type against the third. When the variant arms are full algorithms,
escalate to a Strategy (see `python-applying-design-patterns`).

### Liskov Substitution

If a program uses an abstraction, any implementation of that abstraction must be substitutable without
breaking the program. Here the abstraction is an ABC port and the implementations are its adapters and
its `Spy` doubles. The contract is the signature plus its documented obligations, which live in the
port's docstring (the `:returns:` and `:raises:` fields).

An implementation violates the principle when it raises for a declared operation the contract says
always succeeds (the Python form is `raise NotImplementedError` in a concrete class), demands more than
the contract states (extra setup, a narrower input range), or returns less than promised (a `None`
where the annotation says a value). The caller, holding only the abstraction, cannot defend against
surprises it was told would not happen.

```python
# Bad: a holder of Account cannot trust withdraw, so the abstraction is dishonest here.
class Account(ABC):
    """Balance from which funds are always withdrawable for a positive amount."""

    @abstractmethod
    def withdraw(self, amount: Money) -> Account:
        """Removes the amount from the balance.

        :param amount: The positive amount to remove.
        :returns: The account holding the reduced balance.
        """


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class FrozenAccount(Account):
    balance: Money

    def withdraw(self, amount: Money) -> Account:
        raise OperationNotSupported()  # breaks every caller that relies on the contract


# Good: separate the capability. A frozen account simply does not offer withdraw.
class Account(ABC):
    """Account with a known balance."""

    @abstractmethod
    def balance(self) -> Money:
        """Returns the current balance.

        :returns: The current balance.
        """


class Withdrawable(Account):
    """Account whose funds can be withdrawn."""

    @abstractmethod
    def withdraw(self, amount: Money) -> Withdrawable:
        """Removes the amount from the balance.

        :param amount: The positive amount to remove.
        :returns: The account holding the reduced balance.
        :raises InsufficientFunds: When the balance is below the amount.
        """
```

Python adds one substitution failure the type checker catches for you. An override that narrows a
parameter type breaks the contract, and `mypy --strict` reports it as a Liskov violation. A single
inbound port shared by every use case, `CommandHandler.handle(command: Command)`, forces exactly that
narrowing in each handler, which is why `rules/python-architecture.md` gives every use case its own
inbound port typed on its own command.

```python
# Bad: each handler narrows the parameter, so no handler is substitutable for the port.
class CommandHandler(ABC):
    """Executor of any assignment intent."""

    @abstractmethod
    def handle(self, command: Command) -> None:
        """Carries out the intent.

        :param command: Any assignment intent.
        """


@final
class IssuesAssigningHandler(CommandHandler):

    def handle(self, command: AssignIssues) -> None:  # mypy: violates the Liskov substitution principle
        ...


# Good: one port per use case, typed on its own command. The handler honors it exactly.
class IssuesAssigning(ABC):
    """Assigning of the open issues that have no assignee yet."""

    @abstractmethod
    def handle(self, command: AssignIssues) -> None:
        """Assigns every open issue without an assignee to the assignees the repository accepts.

        :param command: The assignment requested by the actor.
        :raises AssigneesRequired: When no assignee remains and an empty assignment is not allowed.
        :raises SelfAssignmentNotAllowed: When the actor is among the assignees and self-assignment is denied.
        """


@final
class IssuesAssigningHandler(IssuesAssigning):

    def handle(self, command: AssignIssues) -> None:
        ...
```

The classic illustration is Square modeled as a subtype of a mutable Rectangle. Code that sets width
and height independently and expects their product as the area is correct for a Rectangle and wrong for
a Square, because a Square cannot let the two vary. The cure is the same: do not claim an is-a that the
behavior cannot honor. Prefer immutable shapes behind a `Shape` abstraction, which this repository
already mandates for value objects (`rules/python-domain.md`), and `@final` forbids the concrete
subclassing that would set the trap in the first place.

Trade-off: the fix is often to split the abstraction (see Interface Segregation), which multiplies
ports. Split only when an implementation genuinely cannot honor a method, not to chase purity.

### Interface Segregation

No client should be forced to depend on methods it does not use. A wide ABC couples every implementer
to the union of all consumers' needs. The smell is an adapter or a `Spy` that stubs, returns an empty
value, or raises `NotImplementedError` for an abstract method only one other consumer cares about.
Split the ABC into cohesive ports, each centered on one resource, so a client depends only on what it
actually calls.

```python
# Bad: a read-only adapter must stub export_csv to satisfy the ABC.
class AccountStorage(ABC):
    """Accounts kept, looked up, and exported."""

    @abstractmethod
    def save(self, account: Account) -> None:
        """Keeps the account."""

    @abstractmethod
    def find_by_id(self, account_id: AccountId) -> Account | None:
        """Returns the account with the identifier."""

    @abstractmethod
    def export_csv(self) -> bytes:
        """Returns every account encoded as CSV."""  # only the reporting path wants this


# Good: two cohesive ports, each consumer depends on one.
class Accounts(ABC):
    """Accounts kept for later lookup."""

    @abstractmethod
    def save(self, account: Account) -> None:
        """Keeps the account.

        :param account: The account to keep.
        """

    @abstractmethod
    def find_by_id(self, account_id: AccountId) -> Account | None:
        """Returns the account with the identifier.

        :param account_id: The identifier of the account.
        :returns: The account, or None when no account has the identifier.
        """


class AccountExport(ABC):
    """Portable rendering of the account set."""

    @abstractmethod
    def export_csv(self) -> bytes:
        """Returns every account encoded as CSV.

        :returns: The accounts as CSV bytes.
        """
```

Two ports over the same resource with different return shapes are Interface Segregation applied, not
duplication. A read side and a write side are never merged for reuse. In this repository the
outbound ports already stand one per resource (`Issues`, `PullRequests`, `Assignees`), and the driving
side holds one inbound port per use case, so the console driver depends on each use case it starts
and on nothing else.

Trade-off: segment too finely, and you get a cloud of one-method ports that obscure the resource.
Keep each port around one resource and the operations a single consumer naturally needs together.
(Naming a port after its resource in the plural rewards this: a cohesive port names itself.)

### Dependency Inversion

High-level modules should not depend on low-level modules. Both should depend on an abstraction, and
the abstraction belongs to the high-level side. Details depend on policy, never the reverse. In a
hexagon this is exactly the outbound port: the core declares the contract in its own domain terms under
`src/application/ports/outbound`, and the driven adapter in the outer layer implements it explicitly.
The source dependency then points inward, opposite to the flow of control.

```python
# Bad: the handler builds and names a concrete adapter, welded to PyGithub.
@final
class IssuesAssigningHandler(IssuesAssigning):

    def __init__(self, repository: Repository) -> None:
        records = GitHubIssueRecords(repository=repository, triggering_numbers=None)
        # Policy reaching down to a detail.
        self._issues = GitHubIssues(records=records, journal=AssignmentJournal(), repository=repository)


# Good: the handler depends on a port the core owns, the composition root injects the adapter.

# src/application/ports/outbound/issues.py, the abstraction owned by the core.
class Issues(ABC):
    """Open issues of the repository."""

    @abstractmethod
    def unassigned(self) -> tuple[Issue, ...]:
        """Lists the open issues that have no assignee.

        :returns: The open issues without an assignee.
        """

    @abstractmethod
    def assign(self, issue: Issue) -> None:
        """Records the assignees of the issue in the repository.

        :param issue: The issue carrying its granted assignees.
        """


# src/application/handlers/issues_assigning_handler.py, depends on the abstractions only.
@final
class IssuesAssigningHandler(IssuesAssigning):

    def __init__(self, issues: Issues, assignees: Assignees) -> None:
        self._issues = issues
        self._requested_assignment = RequestedAssignment(assignees=assignees)


# src/dependencies.py, the only place that names the concretes.
issue_records = providers.Singleton(
    GitHubIssueRecords,
    repository=repository,
    triggering_numbers=settings.provided.event.issue_numbers
)

issues = providers.Singleton(GitHubIssues, records=issue_records, journal=journal, repository=repository)

assignees = providers.Singleton(GitHubAssignees, repository=repository)

assign_issues = providers.Factory(IssuesAssigningHandler, issues=issues, assignees=assignees)
```

This is the principle that makes the runnable-core test pass: replace every adapter with a hand-written
double (an `IssuesSpy` implementing `Issues`) and the handler still runs, with no network and no token.
The `dependency_injector` container in `src/dependencies.py` binds `GitHubIssues` to `Issues`,
and the handler never learns which implementation it holds. The same inversion governs the driving
side: the console driver depends on the inbound ports, never on a concrete handler. The structural
enforcement (no concrete outer-layer type crossing inward) is owned by `rules/python-architecture.md`
and the `python-applying-hexagonal-architecture` skill.

Trade-off: inversion costs an ABC and a wiring point. Pay it where a boundary or a real second
implementation exists, not for an internal collaborator that will only ever have one form.

## Separation of Concerns

A concern is one dimension of a problem: the business rule, the presentation format, persistence,
transport, validation, logging. Separation of Concerns says each concern lives in its own section with
as little overlap as the design allows, so each can be reasoned about, changed, and tested on its own.
Single Responsibility is SoC applied to a single class (one reason to change), and the hexagon's layers
are SoC applied to the whole action (the domain concern apart from the GitHub concern apart from the
console concern).

```python
# Bad: one method computes the rule, formats the output, and writes the file, three concerns interwoven.
@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MonthlyReport:
    lines: tuple[ReportLine, ...]

    def publish(self, path: Path) -> None:
        total = self._sum_lines()  # business rule
        html = f'<h1>Total: {total}</h1>'  # presentation concern
        path.write_text(html)  # persistence concern


# Good: each concern has its own home, a handler orchestrates them.
@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MonthlyReport:
    lines: tuple[ReportLine, ...]

    def total(self) -> Money:
        ...  # the rule only


@final
class ReportHTMLView:

    def render(self, report: MonthlyReport) -> str:
        ...  # the format only


class Reports(ABC):
    """Rendered reports kept for later reading."""

    @abstractmethod
    def save(self, report: MonthlyReport) -> None:
        """Keeps the report for later reading.

        :param report: The computed report.
        :raises ReportNotSaved: When the report cannot be kept.
        """
```

Trade-off: separated too zealously, a single cohesive step is scattered across files the reader must
reassemble before understanding it. Separate by concern (a different reason to change), not by line.

## High Cohesion

Cohesion measures how well the parts of a module belong together. The strongest form, functional
cohesion, is a module whose every element contributes to one well-defined task. The weakest forms
gather code by accident: a `utils.py` of module-level functions grouped only by being leftovers, or a
`Manager` class that touches everything. High cohesion makes a module easy to name, to change for one
reason, and to test in isolation. This repository bans these generic names outright (the `...Util`,
`...Helper`, and `...Manager` suffixes in `rules/python-code-style.md`, and the `src/utils`,
`src/helpers`, `src/common`, and `src/shared` packages in `rules/python-design-principles.md`), which
pushes you toward cohesion before you have written a line.

```python
# Bad: a grab-bag, the methods share nothing but the module they sit in.
@final
class OrderUtils:

    def total(self, order: Order) -> Money:
        ...  # an order rule

    def format_email(self, customer: Customer) -> str:
        ...  # a presentation concern

    def connect_database(self) -> Connection:
        ...  # an infrastructure concern


# Good: each unit is cohesive around one task.
@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Order:
    lines: tuple[OrderLine, ...]

    def total(self) -> Money:
        ...  # belongs with the order


@final
class CustomerEmailView:

    def render(self, customer: Customer) -> str:
        ...  # belongs with presentation
```

Trade-off: cohesion and coupling trade off against each other in the small. Pushing every method onto
the class that owns its data raises cohesion, but a class that does too much for one actor has crossed
back into a Single Responsibility violation. Cohesion is one task per unit, not all tasks on one unit.

## Loose Coupling

Coupling measures how much one module must know about another. Tight coupling shows up as a change in
one place forcing changes in many (shotgun surgery), an import of a concrete class that cannot be
swapped, or a caller that reaches through an object graph (a Demeter violation). Loose coupling depends
on abstractions the consumer owns, passes data rather than letting callers navigate it, and keeps each
module's public surface small.

The classic ladder ranks how two modules can bind, tightest first. Aim for the bottom rung.

| Coupling form (tightest first) | What binds the two modules                                   | The move toward looser                                                   |
|--------------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------|
| Content                        | One module reaches into another's internals or private state | Tell the neighbor to act, never read its internals (LoD, Tell-Don't-Ask) |
| Control                        | One passes a flag that steers the other's branching          | Split the operation so each path is its own intention-revealing method   |
| Stamp                          | A whole record is passed when only one field is used         | Pass only the value the callee needs                                     |
| Data                           | Only the needed values pass across a narrow contract         | This is the target, an abstraction the consumer owns                     |

Python makes the top rung easy to reach. Nothing stops a caller from reading `report._lines`, and a
single-underscore attribute is a promise, not a lock. Treat any read of another object's underscore
attribute as content coupling, in production code and in tests alike (`rules/python-testing.md`
forbids asserting on a private attribute).

```python
# Bad: control coupling, a boolean steers the callee's branches from outside.
report.render(as_html=True)  # the caller drives the internal branch

# Good: each path is its own intention-revealing operation, the caller couples to data only.
report_html_view.render(report=report)
```

Trade-off: zero coupling is impossible and undesirable, modules must collaborate to do anything. The
goal is the loosest coupling that still lets them work: data coupling across a narrow, owned contract,
never content or control coupling.

## DRY

Every piece of knowledge should have a single, authoritative representation. DRY is about knowledge,
not text. The same business rule coded in two classes is the defect, because a change must then be
made in two places and one will be forgotten. The fix is a single owner, with callers telling it to
act.

```python
# Bad: the overdraft rule is duplicated, the two will drift.
@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Account:
    balance: Money

    def can_withdraw(self, amount: Money) -> bool:
        return self.balance.is_at_least(amount=amount)  # the rule, here


@final
class WithdrawalForm:

    def is_valid(self, amount: Money, account: Account) -> bool:
        return account.balance.is_at_least(amount=amount)  # the same rule, copied


# Good: the rule has one owner, the form asks the owner.
@final
class WithdrawalForm:

    def is_valid(self, amount: Money, account: Account) -> bool:
        return account.can_withdraw(amount=amount)  # the single owner of the rule decides
```

In this repository the canonical case is the self-assignment rule. `Issue` and `PullRequest` both
enforce it, and coding it in both models is exactly the duplication DRY forbids. Its single owner is
the `Assignment` value object in `src/application/domain/models/commons/assignment.py`. Both models take
it in `assign(assignment=...)`, ask it whether it `excludes(author=..., draft=...)` them, and ask it for
`granted_assignees(author=...)`, which raises `AssigneesRequired` or `SelfAssignmentNotAllowed`
(`rules/python-design-principles.md` § DRY).

Two caveats keep DRY from doing harm.

- The wrong abstraction is worse than duplication. Two blocks that look alike but encode different
  rules must not be unified. A shared helper that grows a `bool` keyword or a branch to serve divergent
  callers is the signal. Inline it back into each caller, then re-extract only what is truly shared.
- The rule of three. Mechanical, rule-free code (PyGithub-to-domain translation, request assembly,
  model-to-output conversion) is extracted on the third occurrence, within one layer and one
  technology. The first two sightings stay inline.

Trade-off: chasing DRY across a context boundary couples two models that should evolve apart. Never
share to avoid duplicating across the domain and adapter seam, or across two technologies under
`src/driven/`. Parallel GitHub adapters whose shapes differ keep their own translation, and the
parse-then-construct pair at the driver boundary is defense plus invariant, not duplication. The
rule's § DRY lists both as correct by design.

## KISS

Keep it simple. Of the designs that satisfy the requirement, prefer the one with the fewest moving
parts a reader must hold in their head. Complexity is not free. Every abstraction, layer, generic, and
configuration knob is something to learn, test, and maintain. KISS does not mean primitive, and it is
not clever-in-reverse. It means no accidental complexity layered on top of the problem's essential
complexity. In Python the usual accidental complexity is introspection: `getattr` loops, `__dict__`
walks, metaclasses, and decorators that rewrite signatures, all of which also blind `mypy --strict`.

```python
# Bad: a generic, introspection-driven mechanism for a job that is a single explicit mapping.
@final
class DynamicMapper:

    def map(self, source: object, target_type: type[object]) -> object:
        ...  # getattr over fields, a config of overrides, a cache of metadata


# Good: the explicit mapping, obvious at a glance, checked by the type checker, trivial to change.
@final
@dataclass(frozen=True, slots=True, kw_only=True)
class OrderView:
    total: str
    order_id: str

    @staticmethod
    def from_order(order: Order) -> OrderView:
        return OrderView(total=order.total().amount(), order_id=str(order.order_id))
```

Trade-off: the simplest code today can become the wrong simple if the problem grows. KISS is not an
excuse to skip a boundary the architecture requires, it is a bias against complexity the problem itself
does not demand. When the present problem is genuinely complex, the simplest honest solution is still
complex, and that is allowed.

## YAGNI

You are not going to need it. Do not build a generalization until a real consumer demands it. Every
preventive ABC, hook, keyword parameter, or default is code to read, test, and maintain for a future
that may never arrive, and that often arrives in a shape you did not predict.

```python
# Bad: a pricing seam and a config flag for a single, current behavior.
class OrderPricing(ABC):
    """Price computation for an order."""

    @abstractmethod
    def price_for(self, order: Order) -> Money:
        """Returns the price of the order."""


@final
class OrderPricer:

    def __init__(self, pricing: OrderPricing, use_new_engine: bool) -> None:
        self._pricing = pricing
        self._use_new_engine = use_new_engine


# Good: the one behavior you actually have, extracted later if a second arrives.
@final
class OrderPricer:

    def price_for(self, order: Order) -> Money:
        ...  # the only rule today
```

Trade-off: YAGNI is not an argument against the seams an architecture requires. A port at a real
boundary is not speculative, the dependency rule mandates it (see
`python-applying-hexagonal-architecture`). YAGNI targets flexibility added for an imagined future, not
the structure the present design needs.

## Tell, Don't Ask

Tell an object to do something, do not pull its state out and decide on its behalf. Asking leaks the
rule out of the class that holds the data, and the rule then lives in callers that can drift. Telling
keeps the decision next to the data, where the invariant is enforced once.

```python
# Bad: the caller asks for state, then decides. The rule has left the Account.
if account.status == AccountStatus.ACTIVE and account.balance.is_at_least(amount=amount):
    account = Account(status=account.status, balance=account.balance.subtract(amount=amount))

# Good: the caller tells the Account, which enforces its own invariant and answers.
account = account.withdraw(amount=amount)  # returns the new account, or raises InsufficientFunds
```

Because domain models here are frozen dataclasses, `withdraw` returns a new `Account` and raises a
domain exception on a violated invariant rather than mutating in place. Rebuilding someone else's
model from the outside (the bad path) is exactly the leak the principle warns about, and the
constructor call that yields the next state belongs inside the model's own transition method. In this
repository the handler tells `issue.assign(assignment=...)` to act and hands the result to the
`Issues` port, it never reads the assignees off the issue to decide whether assignment is allowed.

Trade-off: taken to an extreme, Tell-Don't-Ask argues against every attribute read, which is
impractical for read models and serialization. Value objects legitimately expose their fields, and
reads at the boundary (a driven adapter translating a model to a PyGithub call, the console driver
writing the action output) legitimately ask. The principle targets decisions a domain type should own,
not every field access.

## Law of Demeter

A method should talk only to its immediate collaborators: itself, its parameters, values it creates,
and its own attributes. It should not reach through one object to operate on another's internals. The
smell is a train wreck, a chain of accessors that navigates an object graph the caller should not know.
Python hides the chain well, because a dataclass field or a `@property` reads without parentheses, but
`a.b.c` is still three hops.

```python
# Bad: the caller knows Customer has an Account that has a balance with a currency.
currency = customer.account.balance.currency

# Good: ask the nearest object for what you need, let it delegate inward.
currency = customer.billing_currency()
```

Trade-off: the principle applies to behavior, not to data structures and fluent value objects. An
immutable value object chaining transformations (`Money(amount=..., currency=...).add(other=...)`) is
not a violation, because each call returns a peer of the same abstraction rather than reaching into a
stranger's internals.

## Composition over inheritance

Favor assembling behavior from injected collaborators over reusing code through a shared base. Python
has full class inheritance and multiple inheritance, so the temptation is a base class or a mixin
extended only to borrow a method. That couples the subclass to the base's internals, its attributes,
and its method resolution order, for a relationship that is not a true is-a. This repository closes the
door: every concrete class is `@final`, and a class extends only an ABC port it implements or an
exception base (`rules/python-code-style.md` § Classes).

```python
# Bad: inheritance used only to reuse a method, OrderService is not truly an AuditLog.
class AuditLog:

    def write(self, line: str) -> None:
        ...


class OrderService(AuditLog):  # extended only to borrow write()

    def place(self, order: Order) -> None:
        self.write(line='placed')


# Good: inject the collaborator behind an ABC the consumer owns.
class AuditTrail(ABC):
    """Domain events recorded for later inspection."""

    @abstractmethod
    def record(self, event: str) -> None:
        """Appends the event to the trail.

        :param event: The domain event to record.
        :raises EventNotRecorded: When the event cannot be stored.
        """


@final
class OrderService:

    def __init__(self, audit: AuditTrail) -> None:
        self._audit = audit

    def place(self, order: Order) -> None:
        self._audit.record(event='placed')
```

The same move shapes the handlers in this repository. The handler that assigns both pull requests and
issues holds the `Issues`, `PullRequests`, and `Assignees` outbound ports, injected by the composition
root, and builds one `Assignment` for both kinds. It never extends a concrete handler and never invokes
another handler or inbound port. The rule both kinds share lives on the `Assignment` value object
(`rules/python-architecture.md` § Commands and handlers).

Trade-off: composition adds a constructor parameter and a wiring point. That is the price of swappable,
independently testable behavior, and it is almost always worth paying over a base class or mixin
reached for purely to reuse code.

## Sources

- Robert C. Martin, "Design Principles and Design Patterns" (2000), the paper that gathered the five.
  https://web.archive.org/web/20150906155800/http://www.objectmentor.com/resources/articles/Principles_and_Patterns.pdf
- Robert C. Martin, "Clean Code: A Handbook of Agile Software Craftsmanship" (Prentice Hall, 2008),
  for cohesion, function size, and the smells.
- Robert C. Martin, "Clean Architecture: A Craftsman's Guide to Software Structure and Design"
  (Prentice Hall, 2017), the SOLID chapters.
- Robert C. Martin, "The Single Responsibility Principle" (2014).
  https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
- Barbara Liskov and Jeannette Wing, "A Behavioral Notion of Subtyping" (ACM TOPLAS, 1994), the origin
  of the substitution principle.
- Gamma, Helm, Johnson, and Vlissides, "Design Patterns" (1994), for "favor object composition over
  class inheritance".
- Andrew Hunt and David Thomas, "The Pragmatic Programmer" (1999), for DRY, Tell-Don't-Ask, and the
  Law of Demeter (Lieberherr and Holland, 1989).
- Martin Fowler, "TellDontAsk" (https://martinfowler.com/bliki/TellDontAsk.html) and "Yagni"
  (https://martinfowler.com/bliki/Yagni.html).
- Martin Fowler, "Refactoring: Improving the Design of Existing Code" (2nd ed., 2018), for the code
  smells (feature envy, shotgun surgery, divergent change) and the DRY discussion.
- Sandi Metz, "The Wrong Abstraction" (2016).
  https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- Edward Yourdon and Larry Constantine, "Structured Design" (1979), the origin of the coupling and
  cohesion ladders.
- Meilir Page-Jones, "The Practical Guide to Structured Systems Design" (2nd ed., 1988), for the
  coupling and cohesion taxonomy in practice.
- Edsger W. Dijkstra, "On the role of scientific thought" (1974), the origin of "separation of
  concerns".
- Artem Zinnatullin (zakirullin), "Cognitive Load Developer's Handbook", for the working-memory model
  and the intrinsic-versus-extraneous split. https://github.com/zakirullin/cognitive-load
- John Ousterhout, "A Philosophy of Software Design" (2018), for deep versus shallow modules and
  defining complexity as what a reader must hold in their head.
- The enforced specifics are this repository's own, in the rules named under `SKILL.md` § In this
  action.
