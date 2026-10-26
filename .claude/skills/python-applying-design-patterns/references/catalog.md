# GoF pattern catalog

This is the pattern catalog for the `python-applying-design-patterns` skill. It covers all 23 Gang of Four
patterns generically (intent, entry signal, structure, a minimal Python example, the trade-off that bounds it),
then a short note on how each lands in this hexagonal Python action. The examples use domain-neutral names on
purpose, they teach the pattern shape only, and each one follows `rules/python-code-style.md` (full
annotations, `@final`, frozen dataclasses, keyword arguments, no `else`, docstrings on `ABC` ports only). A
`# src/...` comment marks where a module would live when the layer matters. The at-a-glance table below is the
authority for placement here. Read the entry before writing the class. A pattern is a shape, never a class
name: the class keeps its business name (the no-pattern-suffix naming invariant is owned by
`rules/python-code-style.md`, § Naming).

## Contents

- This-action home at a glance
- Creational
- Structural
- Behavioral
- Sources

## This-action home at a glance

| Family     | Pattern                 | In this action                                                                        |
|:-----------|:------------------------|:--------------------------------------------------------------------------------------|
| Creational | Singleton               | A `providers.Singleton` in `src/dependencies.py`, passed by constructor               |
| Creational | Factory Method          | `@staticmethod` named factories on the class (`Result.success()`, `from_options`)     |
| Creational | Abstract Factory        | `src/driven/`, rare, usually a second adapter behind a port chosen in the container   |
| Creational | Builder                 | Tests only, a test data builder under `tests/support/builders/`                       |
| Creational | Prototype               | Provided, a frozen dataclass copies itself through its own constructor                |
| Structural | Adapter                 | The `src/driver/console` and `src/driven/<technology>` layers themselves              |
| Structural | Bridge                  | Provided by ports and adapters                                                        |
| Structural | Composite               | Rare, no recursive hierarchy in this action                                           |
| Structural | Decorator               | `src/driven/` over an outbound port, concern prefix, same `ABC`                       |
| Structural | Facade                  | A handler over several outbound ports, or one adapter over PyGithub                   |
| Structural | Flyweight               | Provided by `StrEnum` and `IntEnum` members                                           |
| Structural | Proxy                   | `src/driven/` over an outbound port, lazy construction left to the container          |
| Behavioral | Chain of Responsibility | Rare, no middleware stack. Prefer a direct call                                       |
| Behavioral | Command                 | `src/application/commands` plus an `<InboundPort>Handler` behind its own inbound port |
| Behavioral | Interpreter             | No special stance                                                                     |
| Behavioral | Iterator                | Provided by `for`, comprehensions, and generators, never hand-rolled                  |
| Behavioral | Mediator                | No special stance                                                                     |
| Behavioral | Memento                 | Rare, the prior frozen instance already is the snapshot                               |
| Behavioral | Observer                | No event bus, the handler calls each outbound port directly                           |
| Behavioral | State                   | Status `StrEnum` first, per-state classes past the threshold                          |
| Behavioral | Strategy                | A domain `ABC` with one `@final` class per variant, an outbound port when I/O varies  |
| Behavioral | Template Method         | No special stance, prefer composition (a `Callable` or a small `ABC`)                 |
| Behavioral | Visitor                 | A read-side projection at a boundary, never the domain. Prefer `match`                |

## Creational

### Singleton

- **Intent**: Ensure a class has exactly one instance and give a global access point to it.
- **Entry signal**: You feel tempted to reach a shared object through a module-level accessor from many places.
- **Structure**: A module holds its only instance and hands it out through an accessor, built on first use.
- **Example** (the hand-rolled form, shown so you recognize it):

```python
from functools import cache

from src.driven.filesystem.file_journal import FileJournal


@cache
def process_journal() -> FileJournal:
    return FileJournal()
```

- **Trade-off**: Global mutable state, hidden coupling, hard to test (you cannot substitute a `Spy`). When one
  instance is all you need, build it once in the composition root and inject it.
- **In this action**: The `dependency_injector` container owns lifecycle. A single instance is a
  `providers.Singleton` declared in `src/dependencies.py` (the PyGithub client, the repository, each
  driven adapter) and handed to its consumers by constructor injection. Never a module-level instance, a
  `functools.cache` accessor, or a `__new__` override. No module outside `src/dependencies.py` imports the container
  (`rules/python-architecture.md` § Composition root).

### Factory Method

- **Intent**: Defer to a method which concrete instance to construct, giving the construction a name.
- **Entry signal**: Construction carries a meaningful name or branches on its input, so a raw constructor call
  reads poorly.
- **Structure**: A named `@staticmethod` on the class returns the product, deciding its concrete shape.
- **Example**:

```python
from dataclasses import dataclass
from enum import StrEnum
from typing import final


@final
class Channel(StrEnum):
    SMS = 'sms'
    EMAIL = 'email'


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Notification:
    body: str
    channel: Channel

    @staticmethod
    def email(body: str) -> Notification:
        return Notification(body=body, channel=Channel.EMAIL)

    @staticmethod
    def sms(body: str) -> Notification:
        return Notification(body=body, channel=Channel.SMS)
```

- **Trade-off**: One more indirection. When construction is a plain constructor call with no name and no
  branch, the factory earns nothing.
- **In this action**: Canonical, as `@staticmethod` factories on the class itself, named for the business
  (`Result.success()`, `Result.assignment_failure(message=...)` on the console result,
  `AssignmentKind.from_options(options=...)` on an enum). A factory names its own class in the return type, never `Self`. The domain declares no default
  values, so each distinct input shape is its own named factory. The GoF subclass-decides form is not used,
  because concrete classes never inherit from each other. See `rules/python-code-style.md` § Classes and
  `rules/python-domain.md`.

### Abstract Factory

- **Intent**: Produce a family of related objects together without naming their concrete classes.
- **Entry signal**: One call must return a matched set of collaborators that cannot be wired independently.
- **Structure**: A factory `ABC` declares one creator per product, each concrete factory builds one consistent
  family.
- **Example**:

```python
# src/application/ports/outbound/theme.py
from abc import ABC, abstractmethod


class Theme(ABC):
    """Widgets drawn in one matched visual style."""

    @abstractmethod
    def button(self) -> Button:
        """
        Builds the button drawn in this style.

        :returns: The styled button.
        """

    @abstractmethod
    def checkbox(self) -> Checkbox:
        """
        Builds the checkbox drawn in this style.

        :returns: The styled checkbox.
        """


# src/driven/dark/dark_theme.py
from typing import final


@final
class DarkTheme(Theme):

    def button(self) -> Button:
        return DarkButton()

    def checkbox(self) -> Checkbox:
        return DarkCheckbox()
```

- **Trade-off**: Many classes for a small gain, and a new product means touching every factory. When each member
  can be wired independently in the composition root, a factory class only duplicates that wiring.
- **In this action**: Lives in `src/driven/`, but rarely needed. Most provider variation is a second adapter
  behind the same outbound port, chosen in `src/dependencies.py` (a wiring-only selection, for example a
  `providers.Selector` keyed by a setting). Reach for the factory only when one call must return a matched set.

### Builder

- **Intent**: Assemble a complex object step by step, separating construction from the final representation.
- **Entry signal**: Many optional parts, or an object graph with sensible defaults you want to override a few at a
  time.
- **Structure**: A builder accumulates parts through `with_...` steps that each return a new builder, and a final
  `build()` returns the assembled product.
- **Example**:

```python
# tests/support/builders/report_builder.py
from dataclasses import dataclass
from typing import final

from src.application.domain.models.report import Report


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ReportBuilder:
    rows: tuple[str, ...] = ()
    title: str = 'Untitled'

    def with_rows(self, *rows: str) -> ReportBuilder:
        return ReportBuilder(rows=rows, title=self.title)

    def with_title(self, title: str) -> ReportBuilder:
        return ReportBuilder(rows=self.rows, title=title)

    def build(self) -> Report:
        return Report(rows=self.rows, title=self.title)
```

- **Trade-off**: An extra class and indirection. For an object with few required fields, a keyword-only
  dataclass constructor already covers the need, so a builder is overkill.
- **In this action**: Tests only, as the Test Data Builder shape under `tests/support/builders/` (a frozen
  dataclass whose steps return a copy through its constructor, so a step never mutates the caller's
  builder). It is the one place defaults live in test code and the one place the `Builder` suffix is legitimate.
  Reach for it past roughly five construction parameters or when the instance is reused across modules.
  Production construction uses the dataclass constructor and the named factories. See `rules/python-testing.md`
  § Fixtures and builders and the `python-writing-tests` skill.

### Prototype

- **Intent**: Create new objects by copying an existing instance rather than constructing from scratch.
- **Entry signal**: Copying a configured instance is cheaper or simpler than building one anew.
- **Structure**: The copy carries every field of the original except the few that change.
- **Example**:

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Money:
    amount: Decimal
    currency: Currency

    def with_amount(self, amount: Decimal) -> Money:
        return Money(amount=amount, currency=self.currency)
```

- **Trade-off**: Shallow versus deep copy is easy to get wrong when a field holds a mutable collection. When
  construction is cheap and explicit, copying hides intent.
- **In this action**: Already provided. Domain models are frozen dataclasses holding only `tuple` or `frozenset`
  collections, so `Issue(number=issue.number, author=issue.author, assignees=assignees)` yields a safe copy and the
  original stays untouched. `dataclasses.replace` is not used, because analyzers type its result as
  `DataclassInstance`. Never `copy.copy`, `copy.deepcopy`, or a hand-written `clone`. See `rules/python-domain.md` §
  Models and value objects.

## Structural

### Adapter

- **Intent**: Convert one interface into another so an existing class fits the contract a caller expects.
- **Entry signal**: You wrap an external API or library whose shape does not match your own port.
- **Structure**: An adapter implements your target `ABC` explicitly and translates each call onto the adaptee.
- **Example**:

```python
# src/application/ports/outbound/mailer.py
from abc import ABC, abstractmethod


class Mailer(ABC):
    """Outgoing mail addressed to one recipient."""

    @abstractmethod
    def send(self, body: str, recipient: str) -> None:
        """
        Sends the message body to the recipient.

        :param body: The message text.
        :param recipient: The address that receives the message.
        :raises MailUnavailable: When the mail provider refuses the delivery.
        """


# src/driven/vendor/vendor_mailer.py
from typing import final

from vendor_sdk import VendorClient, VendorError, VendorMessage


@final
class VendorMailer(Mailer):

    def __init__(self, client: VendorClient) -> None:
        self._client = client

    def send(self, body: str, recipient: str) -> None:
        message = VendorMessage(text=body, recipient=recipient)

        try:
            self._client.dispatch(message=message)
        except VendorError as dispatch_failure:
            raise MailUnavailable() from dispatch_failure
```

- **Trade-off**: One more layer to maintain. When the external interface already matches your needs, an adapter
  is just a passthrough.
- **In this action**: Canonical. The `src/driver/console` (driving) and `src/driven/<technology>` (driven) layers
  are themselves the Adapter, and implementation is explicit (`class GitHubIssues(Issues)`). Real homes:
  `GitHubIssues`, `GitHubPullRequests`, and `GitHubAssignees` in `src/driven/github` translate PyGithub objects
  and `PaginatedList` into domain models, and catch `GithubException` to re-raise `GitHubRequestFailed`, the typed
  exception the package owns, chained with `from`, never an empty result. No PyGithub type crosses a port. The
  adapter is tested against a `Spy` of the PyGithub `Repository` seam. See the
  `python-applying-hexagonal-architecture` skill and `rules/python-architecture.md` § Driven adapter conventions.

### Bridge

- **Intent**: Split an abstraction from its implementation so the two can vary independently.
- **Entry signal**: Both an abstraction and its implementation grow along separate axes and a class explosion
  looms.
- **Structure**: An abstraction holds a reference to an implementor `ABC` and delegates the varying work to it.
- **Example**:

```python
from abc import ABC, abstractmethod
from typing import final


class Renderer(ABC):
    """A surface that draws plane figures."""

    @abstractmethod
    def draw_circle(self, radius: float) -> str:
        """
        Draws a circle of the given radius.

        :param radius: The circle radius.
        :returns: The drawn figure.
        """


@final
class Circle:

    def __init__(self, radius: float, renderer: Renderer) -> None:
        self._radius = radius
        self._renderer = renderer

    def draw(self) -> str:
        return self._renderer.draw_circle(radius=self._radius)
```

- **Trade-off**: Upfront indirection that pays off only when both axes truly vary. With a single implementation,
  it is needless structure.
- **In this action**: Satisfied. Ports and adapters already decouple abstraction from implementation along the
  I/O axis, and composition over inheritance (`rules/python-design-principles.md` § Precedence) leaves no
  abstract base class to bridge, so there is no separate Bridge construct.

### Composite

- **Intent**: Compose objects into part-whole trees and treat leaves and compositions uniformly.
- **Entry signal**: A genuine recursive hierarchy must be handled the same way at every node.
- **Structure**: A component `ABC` is implemented by both leaves and composites, the composite holds children of
  the same `ABC`.
- **Example**:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final


class FileNode(ABC):
    """A node of a file tree that occupies disk space."""

    @abstractmethod
    def size(self) -> int:
        """
        Measures the space the node occupies.

        :returns: The size in bytes.
        """


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class FileLeaf(FileNode):
    byte_count: int

    def size(self) -> int:
        return self.byte_count


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Folder(FileNode):
    children: tuple[FileNode, ...]

    def size(self) -> int:
        return sum(child.size() for child in self.children)
```

- **Trade-off**: A uniform interface can blur leaf-only and composite-only operations. When nesting is shallow or
  fixed, flat rows plus a parent reference are simpler.
- **In this action**: Rare. Issues, pull requests, and assignees are flat collections, so no recursive hierarchy
  exists today. If one appears, the tree is assembled from flat rows inside a driven adapter, and inside the
  domain it respects the model boundary.

### Decorator

- **Intent**: Attach added behavior to an object by wrapping it, keeping the same interface.
- **Entry signal**: A cross-cutting concern (cache, retry, log, metrics) must wrap a component without editing it.
- **Structure**: A decorator implements the component `ABC` and holds an inner component it delegates to, adding
  behavior around the call.
- **Example**:

```python
# src/application/ports/outbound/journal.py
from abc import ABC, abstractmethod


class Journal(ABC):
    """A running record of what the action did."""

    @abstractmethod
    def write(self, message: str) -> None:
        """
        Appends the message to the record.

        :param message: The line to append.
        """


# src/driven/clock/timestamped_journal.py
from collections.abc import Callable
from datetime import datetime
from typing import final


@final
class TimestampedJournal(Journal):

    def __init__(self, clock: Callable[[], datetime], origin: Journal) -> None:
        self._clock = clock
        self._origin = origin

    def write(self, message: str) -> None:
        moment = self._clock().isoformat()
        self._origin.write(message=f'[{moment}] {message}')
```

- **Trade-off**: Many small wrappers can be hard to trace at runtime. When only one implementation will ever
  exist, fold the behavior in directly. Python's `@` syntax (with `functools.wraps`) decorates a function, not an
  object behind a port: it hides the wrapping from the composition root, so it is not the GoF Decorator here.
- **In this action**: Lives in `src/driven/` over an outbound port, as a `@final` class implementing the same
  `ABC`, concern as prefix and the port capability preserved (for example a `CachedAssignees(Assignees)` over
  `GitHubAssignees`). Wiring is declared in `src/dependencies.py`, outermost concern first, the inner
  adapter injected as a provider. No pattern-name suffix (see `rules/python-code-style.md`, § Naming).

### Facade

- **Intent**: Provide one simple entry point over a complex subsystem.
- **Entry signal**: Callers must orchestrate several objects or steps you would rather hide behind a single call.
- **Structure**: A facade exposes a small surface and coordinates the subsystem objects behind it.
- **Example**:

```python
from typing import final


@final
class MediaConverter:

    def __init__(self, mixer: AudioMixer, writer: FileWriter, encoder: VideoEncoder) -> None:
        self._mixer = mixer
        self._writer = writer
        self._encoder = encoder

    def convert(self, source: str, target: str) -> None:
        audio = self._mixer.extract(source=source)
        video = self._encoder.encode(source=source)

        self._writer.write(audio=audio, video=video, target=target)
```

- **Trade-off**: A facade can grow into a catch-all if it accretes unrelated calls. When the subsystem is one
  object, the facade is just a passthrough.
- **In this action**: Already provided by the shape of the layers. The `PullRequestsAndIssuesAssigningHandler` fronts
  the `PullRequests`, `Issues`, and `Assignees` outbound ports behind one `handle(command)`, and each
  `src/driven/github` adapter fronts the multi-call PyGithub surface behind one port. Do not add a redundant facade
  over a single adapter or a single port, and never one handler over other handlers.

### Flyweight

- **Intent**: Share immutable instances to support large numbers of fine-grained objects efficiently.
- **Entry signal**: A huge number of objects share the same intrinsic state and memory pressure is real.
- **Structure**: Shared instances are keyed by intrinsic state, the extrinsic state is passed in per call.
- **Example**:

```python
from enum import StrEnum
from typing import final


@final
class Glyph(StrEnum):
    LETTER_A = 'a'
    LETTER_B = 'b'

    def render_at(self, row: int, column: int) -> str:
        return f'{self.value} at ({row},{column})'
```

- **Trade-off**: A sharing pool adds complexity and is pointless without real memory pressure. Premature pooling
  trades clarity for nothing.
- **In this action**: Satisfied. `StrEnum` and `IntEnum` members are shared by definition (the intrinsic state),
  parsed through a `@staticmethod` `from_raw` per `rules/python-domain.md` § Enums, and the console exit `Code` is
  an `IntEnum`. No manual instance pool, no interning cache.

### Proxy

- **Intent**: Provide a stand-in that controls access to another object behind the same interface.
- **Entry signal**: You need access guarding, a remote stand-in, or otherwise controlled access, with the same
  surface as the target.
- **Structure**: A proxy implements the subject `ABC` and holds the real subject, mediating each call.
- **Example**:

```python
from typing import final


@final
class ProtectedImage(Image):

    def __init__(self, origin: Image, policy: AccessPolicy) -> None:
        self._origin = origin
        self._policy = policy

    def render(self) -> str:
        if not self._policy.allows():
            raise AccessDenied()

        return self._origin.render()
```

- **Trade-off**: Same shape as Decorator, so the intent is easy to confuse. When you only need deferred
  construction, the container already covers it, so no hand-written proxy.
- **In this action**: Lives in `src/driven/` over an outbound port, same rules as Decorator. A guard raises a
  typed exception the adapter package owns, never a sentinel (`rules/python-code-style.md` § Exceptions). Lazy
  initialization is left to `dependency_injector`, whose providers construct on first resolution, so do not
  hand-write a lazy proxy.

## Behavioral

### Chain of Responsibility

- **Intent**: Pass a request along a chain of handlers until one of them handles it.
- **Entry signal**: A pipeline where each stage may handle the request or pass it to the next.
- **Structure**: Each stage holds the next, it either acts or delegates onward.
- **Example**:

```python
from abc import ABC, abstractmethod
from typing import final


class RequestStage(ABC):
    """A stage a request crosses on its way to a response."""

    @abstractmethod
    def admit(self, request: Request) -> Response:
        """
        Answers the request or passes it to the next stage.

        :param request: The incoming request.
        :returns: The response for the request.
        """


@final
class TokenGuard(RequestStage):

    def __init__(self, next_stage: RequestStage) -> None:
        self._next_stage = next_stage

    def admit(self, request: Request) -> Response:
        if not request.has_token():
            return Response.unauthorized()

        return self._next_stage.admit(request=request)
```

- **Trade-off**: A request can fall off the end unhandled, and the order is implicit. For a fixed two-step flow,
  a direct call is clearer.
- **In this action**: Rare, and there is no middleware stack here. A GitHub Action invocation runs one use case
  and returns one exit `Code`, so prefer a direct ordered call. Do not build a general in-domain handler chain.

### Command

- **Intent**: Turn a request into a standalone object carrying everything needed to perform it.
- **Entry signal**: You need to queue, log, undo, or decouple the invoker from the receiver of a request.
- **Structure**: A command object carries the parameters, a receiver behind its own contract performs it.
- **Example**:

```python
# src/application/commands/send_report.py
from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SendReport:
    recipient: str
    report_number: int


# src/application/ports/inbound/report_sending.py
from abc import ABC, abstractmethod


class ReportSending(ABC):
    """Delivery of a finished report to its recipient."""

    @abstractmethod
    def handle(self, command: SendReport) -> None:
        """
        Delivers the requested report to its recipient.

        :param command: The report request to deliver.
        :raises MailUnavailable: When the mail provider refuses the delivery.
        """


# src/application/handlers/report_sending_handler.py
from typing import final


@final
class ReportSendingHandler(ReportSending):

    def __init__(self, mailer: Mailer, reports: Reports) -> None:
        self._mailer = mailer
        self._reports = reports

    def handle(self, command: SendReport) -> None:
        report = self._reports.find(number=command.report_number)

        body = report.render()
        self._mailer.send(body=body, recipient=command.recipient)
```

- **Trade-off**: A dedicated class per action. For a direct synchronous call with no queueing or logging need, a
  plain function is enough, but here the command and handler pair is the fixed shape of every use case.
- **In this action**: Canonical, as a command and handler pair. Each command (`AssignIssues`,
  `AssignPullRequests`, `AssignPullRequestsAndIssues`) is a `@final` frozen dataclass in `src/application/commands`
  holding primitives only, which the handler promotes into value objects (`Login(value=command.actor)`) through
  `RequestedAssignment`. Each has its own inbound port in `src/application/ports/inbound`, named as the subject
  followed by the gerund (`IssuesAssigning`), with one `handle(self, command: X) -> None`, implemented by a `@final`
  `<InboundPort>Handler` (`IssuesAssigningHandler`) in `src/application/handlers`. The console driver builds the
  command and calls the inbound port (choosing the use case through a dispatch `dict` or `match`, never an `if`
  chain), and a handler never invokes another handler or inbound port. There is NO command bus and NO generic
  `handle(command: Command)` port, which would be a Liskov violation. The three commands share their fields through
  the non-final base `AssignmentCommand`, which `RequestedAssignment.from_command` reads, while each inbound port
  stays typed on its own `@final` subclass. See `rules/python-architecture.md` § Commands and handlers.

### Interpreter

- **Intent**: Define a grammar for a small language and evaluate its sentences.
- **Entry signal**: A recurring expression or grammar (a filter, a rule string) must be parsed and evaluated.
- **Structure**: Each grammar rule is a class implementing one evaluation method, composed into an expression
  tree.
- **Example**:

```python
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import final


class Expression(ABC):
    """A rule evaluated against named readings."""

    @abstractmethod
    def matches(self, readings: Mapping[str, int]) -> bool:
        """
        Tells whether the readings satisfy the rule.

        :param readings: The current reading per name.
        :returns: The verdict of the rule over the readings.
        """


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GreaterThan(Expression):
    name: str
    threshold: int

    def matches(self, readings: Mapping[str, int]) -> bool:
        return readings[self.name] > self.threshold
```

- **Trade-off**: A class per rule grows fast, and a real language outgrows it. For anything nontrivial, a parser
  library beats a hand-rolled interpreter.
- **In this action**: No special stance, apply the generic guidance.

### Iterator

- **Intent**: Traverse the elements of a collection without exposing its underlying representation.
- **Entry signal**: You need custom traversal over a collection while hiding how it is stored.
- **Structure**: The collection produces a sequence the caller loops over, through a generator.
- **Example**:

```python
from collections.abc import Iterator
from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Pages:
    titles: tuple[str, ...]

    def __iter__(self) -> Iterator[str]:
        yield from self.titles
```

- **Trade-off**: Hand-rolling stateful iteration (`__next__` plus `StopIteration`) is error-prone. When the
  language already iterates, a custom iterator class is wasted code.
- **In this action**: Satisfied by the language. Use `for`, comprehensions, a generator function, or a
  `__iter__` that yields, with `collections.abc.Iterable` or `Iterator` in signatures, never a hand-written
  iterator class. PyGithub's lazy `PaginatedList` is consumed inside `src/driven/github` and handed across the
  port as a `tuple` of domain models.

### Mediator

- **Intent**: Centralize how a set of objects interact so they do not refer to each other directly.
- **Entry signal**: Many-to-many coupling between objects you want to collapse into one coordinator.
- **Structure**: Colleagues talk to a mediator, the mediator routes the interaction between them.
- **Example**:

```python
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import final


@final
class FormEvent(StrEnum):
    NAME_FILLED = 'name-filled'
    NAME_CLEARED = 'name-cleared'


class FormEvents(ABC):
    """Events raised by the fields of a form."""

    @abstractmethod
    def notify(self, event: FormEvent) -> None:
        """
        Routes the event to the fields that react to it.

        :param event: The event a field raised.
        """


@final
class SignupForm(FormEvents):

    def __init__(self, submit: Button) -> None:
        self._submit = submit

    def notify(self, event: FormEvent) -> None:
        match event:
            case FormEvent.NAME_FILLED:
                self._submit.enable()
            case FormEvent.NAME_CLEARED:
                self._submit.disable()
```

- **Trade-off**: The mediator can become a catch-all that knows too much. With only two colleagues, a direct
  reference is simpler.
- **In this action**: No special stance, apply the generic guidance.

### Memento

- **Intent**: Capture an object's internal state so it can be restored later, without breaking encapsulation.
- **Entry signal**: An in-memory undo or snapshot of an object's state is a real requirement.
- **Structure**: The originator produces a memento of its state and later restores from one, the memento stays
  opaque to others.
- **Example**:

```python
from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Draft:
    content: str


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Editor:
    content: str

    def snapshot(self) -> Draft:
        return Draft(content=self.content)

    def restore(self, draft: Draft) -> Editor:
        return Editor(content=draft.content)
```

- **Trade-off**: Snapshots can be large and easy to leak state through. When the prior state can be re-read from
  its store, a memento is redundant.
- **In this action**: Rare, and mostly provided. Every transition on a frozen model returns a new instance
  (`issue.assign(...)` leaves `issue` untouched), so holding the prior reference already is the snapshot. A
  dedicated memento is admitted only when a model must expose a narrower snapshot than itself, owned by the
  model (`snapshot()` and `restore()`). When the prior state can be re-read from GitHub, prefer that.

### Observer

- **Intent**: Notify all dependents automatically when a subject's state changes.
- **Entry signal**: One state change must fan out to many independent reactions.
- **Structure**: A producer emits values, consumers react without the producer knowing them concretely.
- **Example**:

```python
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import final


class LineWatcher(ABC):
    """A reader of each output line as it appears."""

    @abstractmethod
    def on_line(self, line: str) -> None:
        """
        Reacts to one output line.

        :param line: The line just produced.
        """


@final
class OutputStream:

    def __init__(self, watchers: Iterable[LineWatcher]) -> None:
        self._watchers = tuple(watchers)

    def publish(self, line: str) -> None:
        for watcher in self._watchers:
            watcher.on_line(line=line)
```

- **Trade-off**: Notification order and cascades can be hard to follow, and a slow observer blocks the producer.
  For a single known reaction, a direct call is clearer. A mutable `subscribe` breaks the assign-once rule for
  service state, so observers arrive by constructor injection.
- **In this action**: No standing home. There are no domain events and no event bus: the action runs one use case
  per invocation, and the handler hands each outcome to its outbound port directly. The standard `logging`
  module already fans a log record out to its handlers, so do not hand-build that either.

### State

- **Intent**: Let an object alter its behavior when its internal state changes, as if it changed class.
- **Entry signal**: An object behaves differently across several states over several operations.
- **Structure**: A state type declares the operations, the context delegates to its current state, transitions
  move between states.
- **Example**:

```python
from enum import StrEnum
from typing import final


@final
class DoorStatus(StrEnum):
    OPEN = 'open'
    CLOSED = 'closed'
    LOCKED = 'locked'

    def is_locked(self) -> bool:
        return self is DoorStatus.LOCKED

    def toggle(self) -> DoorStatus:
        match self:
            case DoorStatus.OPEN:
                return DoorStatus.CLOSED
            case DoorStatus.CLOSED:
                return DoorStatus.OPEN
            case DoorStatus.LOCKED:
                return DoorStatus.LOCKED
```

- **Trade-off**: Per-state classes multiply fast. Below a few states across a few operations, a status enum with
  predicate and transition methods is the simpler form.
- **In this action**: A status `StrEnum` with predicate and transition methods first (`<model>_status.py` under
  `src/application/domain/models`, parsed by a `from_raw` `@staticmethod` per `rules/python-domain.md` § Enums),
  behavior that varies per member as a method on the enum, never an `if` chain at the call site. Per-state
  classes only when three or more states diverge across three or more operations, each a `@final` frozen
  dataclass implementing one domain `ABC`, named by the business state.

### Strategy

- **Intent**: Define a family of interchangeable algorithms behind one interface and choose one at runtime.
- **Entry signal**: A conditional chooses between full algorithm variants from a closed set.
- **Structure**: A strategy `ABC` declares the operation, one class per algorithm, the caller holds the chosen
  one.
- **Example**:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import final


class ShippingFee(ABC):
    """The fee charged to ship a parcel."""

    @abstractmethod
    def for_weight(self, grams: int) -> Decimal:
        """
        Computes the fee for a parcel of the given weight.

        :param grams: The parcel weight in grams.
        :returns: The fee to charge.
        """


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WeightedFee(ShippingFee):
    rate_per_gram: Decimal

    def for_weight(self, grams: int) -> Decimal:
        return self.rate_per_gram * grams


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CappedFee(ShippingFee):
    ceiling: Decimal
    rate_per_gram: Decimal

    def for_weight(self, grams: int) -> Decimal:
        return min(self.rate_per_gram * grams, self.ceiling)
```

- **Trade-off**: A class per variant for a one-line difference is overkill. A small `match` or dispatch `dict`
  inside its owner reads fine until the arms grow into full algorithms. A single-method strategy can be a plain
  `Callable` instead of an `ABC`.
- **In this action**: Lives in `src/application/domain/models` when the variants are business algorithms (a
  domain `ABC` with one `@final` class per variant, or a per-member method on a `StrEnum`). When the variants
  differ by I/O, the strategy is an outbound port with one driven adapter per variant, selected in
  `src/dependencies.py`. The Specification variant is a business-named predicate method on a model
  (`is_`, `has_`, `belongs_to`), and a rule `Issue` and `PullRequest` share (the self-assignment rule over an
  assignee list) lives once in the `Assignment` value object under `models/commons/`, never duplicated across both. See
  `rules/python-design-principles.md` and the `python-applying-design-principles` skill.

### Template Method

- **Intent**: Fix the skeleton of an algorithm in one place and defer a few steps to a collaborator.
- **Entry signal**: A stable sequence repeats with only a few steps varying.
- **Structure**: A function defines the algorithm and calls the varying step through an injected `Callable` or a
  small `ABC`.
- **Example**:

```python
from collections.abc import Callable


def render_report(body: Callable[[], str]) -> str:
    return f'{render_header()}{body()}{render_footer()}'
```

- **Trade-off**: The classic form (an abstract base class with a concrete skeleton and abstract hooks) couples
  the steps to a base class and resists change. Injecting the varying step keeps the steps free to vary
  independently.
- **In this action**: No special stance, but the base-class form is excluded: a class extends only an `ABC` port
  it implements, never a base class for reuse (`rules/python-code-style.md` § Classes). Fix the skeleton in a
  function or a `@final` class and pass the varying step as a `Callable` or a small `ABC`.

### Visitor

- **Intent**: Add a new operation over a stable object structure without changing its classes.
- **Entry signal**: A new operation must traverse a stable type set and does not belong on each class.
- **Structure**: Each element accepts a visitor and dispatches to the method for its class, the visitor carries
  the operation.
- **Example**:

```python
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final


class Shape(ABC):
    """A plane figure that takes a measurement."""

    @abstractmethod
    def accept(self, measure: ShapeMeasure) -> float:
        """
        Hands the shape to the measurement for its kind.

        :param measure: The measurement to take.
        :returns: The measured quantity.
        """


class ShapeMeasure(ABC):
    """A quantity measured over each kind of shape."""

    @abstractmethod
    def of_circle(self, circle: Circle) -> float:
        """
        Measures a circle.

        :param circle: The circle to measure.
        :returns: The measured quantity.
        """

    @abstractmethod
    def of_square(self, square: Square) -> float:
        """
        Measures a square.

        :param square: The square to measure.
        :returns: The measured quantity.
        """


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Circle(Shape):
    radius: float

    def accept(self, measure: ShapeMeasure) -> float:
        return measure.of_circle(circle=self)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Square(Shape):
    side: float

    def accept(self, measure: ShapeMeasure) -> float:
        return measure.of_square(square=self)


@final
class Area(ShapeMeasure):

    def of_circle(self, circle: Circle) -> float:
        return math.pi * circle.radius ** 2

    def of_square(self, square: Square) -> float:
        return square.side ** 2
```

- **Trade-off**: Adding a new element class forces a change to every visitor. For a closed set, a `match` over
  class patterns (`case Circle(radius=radius)`) inside the owner is simpler than the double dispatch.
- **In this action**: Lives only at a boundary (a read-side projection or a reporting adapter), never inside the
  domain. For a closed set, prefer a `match` over class patterns inside the owner.

## Sources

Gamma, Helm, Johnson, Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software"
(1994). Refactoring Guru, "Design Patterns".
