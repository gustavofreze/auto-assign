---
name: python-applying-design-patterns
description: Apply a Gang of Four design pattern, all 23. Triggers on design pattern, Singleton, Factory Method, Abstract Factory, Builder, Prototype, Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy, Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor. Use when choosing whether a pattern fits, or confirming its placement and naming, in any layer of this Python action.
---

# Design patterns (Gang of Four)

A reference for the 23 GoF patterns. A pattern is a named solution to a recurring design problem, a shape,
never a class name. This skill covers every pattern generically (intent, the problem it solves, the entry
signal) and then how each lands in this hexagonal Python action. It is intent-triggered, consulted while
CHOOSING a pattern, never injected into every file.

This skill is not a mandate to use patterns. Most code needs none. Reach for one only when its entry signal
appears, then keep the class named for the business, not the pattern (owned and enforced by
`rules/python-code-style.md` § Naming: no pattern-name suffix). For the layer a pattern belongs in, see
`python-applying-hexagonal-architecture`. For the SOLID pressure that pushes you toward one, see
`python-applying-design-principles`.

## When to use (and when NOT to)

| Use when                                                                        | Skip when                                                                         |
|---------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| A recurring design problem matches a known pattern's intent                     | A one-off with no recurrence, write the straight-line code                        |
| A growing conditional, a duplicated rule, or repeated wiring you want to remove | No entry signal yet, a pattern added preventively is speculative complexity       |
| You want to confirm the placement and naming of a pattern you already see       | The language, the standard library, or the container gives it (§ Already given)   |
| The variant arms have grown into full algorithms behind one `ABC`               | A small `match` or dispatch `dict` inside its owner still reads fine, leave it    |

**Start simple. Reach for a pattern only when its signal appears, never preventively.**

## The 23 patterns

Intent and entry signal for each. The full structure, a generic Python example, the trade-off, and the
this-action note are in `references/catalog.md`.

### Creational (object construction)

| Pattern          | Intent                                       | Reach for it when                                                              |
|------------------|----------------------------------------------|--------------------------------------------------------------------------------|
| Singleton        | One instance, global access                  | Almost never by hand, declare a `providers.Singleton` in `src/dependencies.py` |
| Factory Method   | Defer which type to instantiate to a method  | Construction has a meaningful name or branches by input                        |
| Abstract Factory | Produce a family of related objects together | One call must return a matched set that cannot be wired independently          |
| Builder          | Assemble a complex object step by step       | Many optional parts or a graph with sensible defaults (tests)                  |
| Prototype        | Create by copying an existing instance       | Copy is cheaper than construction, almost never by hand                        |

### Structural (composition)

| Pattern   | Intent                                            | Reach for it when                                                   |
|-----------|---------------------------------------------------|---------------------------------------------------------------------|
| Adapter   | Make an incompatible interface fit a port         | Wrapping an external API or library behind your own outbound port   |
| Bridge    | Split abstraction from implementation on two axes | Both an abstraction and its implementation vary independently       |
| Composite | Treat a part-whole tree uniformly                 | A genuine recursive hierarchy handled the same at every node        |
| Decorator | Add behavior by wrapping, same interface          | A cross-cutting concern (cache, retry, log) wraps without editing   |
| Facade    | One simple entry over a complex subsystem         | Hiding a multi-step or multi-object subsystem behind one call       |
| Flyweight | Share immutable instances to save memory          | A huge number of objects share intrinsic state                      |
| Proxy     | A stand-in controlling access to a target         | Access guarding, lazy loading, or a remote stand-in, same interface |

### Behavioral (responsibility and communication)

| Pattern                 | Intent                                                   | Reach for it when                                                    |
|-------------------------|----------------------------------------------------------|----------------------------------------------------------------------|
| Chain of Responsibility | Pass a request along handlers until one acts             | A pipeline where each stage may handle or pass on                    |
| Command                 | Turn a request into an object                            | Queue, log, undo, or decouple invoker from receiver                  |
| Interpreter             | Evaluate sentences in a small language                   | A recurring grammar or expression to evaluate                        |
| Iterator                | Traverse a collection without exposing it                | Custom traversal, usually `for` or a generator already gives it      |
| Mediator                | Centralize how a set of objects interact                 | Many-to-many object coupling you want to collapse                    |
| Memento                 | Capture and restore state without breaking encapsulation | Undo or snapshot of an object's internal state                       |
| Observer                | Notify dependents when state changes                     | One change must fan out to many reactions                            |
| State                   | Behavior changes with internal state                     | An object behaves differently across several states and operations   |
| Strategy                | Interchangeable algorithm chosen at runtime              | A closed set of full-algorithm variants behind one `ABC`             |
| Template Method         | Fix an algorithm skeleton, defer steps                   | A stable sequence with a few varying steps                           |
| Visitor                 | Add an operation to a structure without changing it      | A new operation over a stable type hierarchy, at a boundary          |

## Problem to pattern (quick index)

| The signal you feel                                             | Pattern                            |
|-----------------------------------------------------------------|------------------------------------|
| A big conditional choosing between full algorithms              | Strategy                           |
| A business rule (eligibility, validity) reused across use cases | Specification (a Strategy variant) |
| Behavior diverges per status across several operations          | State                              |
| A cross-cutting concern must wrap an existing component         | Decorator (or Proxy for access)    |
| An external API shape does not match my outbound port           | Adapter                            |
| A new operation must traverse a stable structure                | Visitor                            |
| One change must notify many reactions                           | Observer                           |
| A request must be queued, logged, or undone                     | Command                            |
| A complex object needs flexible step-by-step assembly           | Builder                            |
| A recursive part-whole tree handled uniformly                   | Composite                          |

## Already given (do not hand-build in this action)

The language, the standard library, or the `dependency_injector` container already provides these. Reaching
for them by hand is the anti-pattern.

| Pattern   | Use instead                                                                                                                                                                                |
|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Singleton | A `providers.Singleton` in the container in `src/dependencies.py`, handed out by constructor injection. No module-level instance, no `functools.cache` accessor, no `__new__` override     |
| Prototype | Frozen dataclasses copy through their own constructor, naming every field. Never `dataclasses.replace`, `copy.copy`, `copy.deepcopy`, or a hand-written `clone` (`rules/python-domain.md`) |
| Iterator  | `for`, comprehensions, and generator functions (`yield`), with `collections.abc.Iterable` or `Iterator` in signatures. Never a hand-written class with `__next__`                          |
| Bridge    | Outbound ports (`src/application/ports/outbound`) and driven adapters already decouple abstraction from implementation, see `python-applying-hexagonal-architecture`                       |
| Flyweight | `StrEnum` and `IntEnum` members are shared instances by definition (`rules/python-domain.md` § Enums)                                                                                      |
| Facade    | A single driven adapter over PyGithub (`GitHubIssues`), a handler over several outbound ports, or the container itself already fronts a multi-step subsystem                               |

## In this action (the overlay)

The patterns above are universal. Their placement and naming here are opinionated:

| Pattern                  | Where it lands in this action                                                                                                                                                                                                                                                                                                                              |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Adapter                  | `src/driven/github`. `GitHubIssues`, `GitHubPullRequests`, and `GitHubAssignees` each wrap PyGithub behind one outbound port in `src/application/ports/outbound` (`Issues`, `PullRequests`, `Assignees`), `src/driven/environment` adapts the action inputs (`ActionSettings`), and `src/driver/console` is the driving adapter                            |
| Command                  | `src/application/commands` plus a handler behind an inbound port. Each command (`AssignIssues`, `AssignPullRequests`, `AssignPullRequestsAndIssues`) is a frozen dataclass of primitives with its own port in `src/application/ports/inbound` and one `handle(command)`, served by an `<InboundPort>Handler` in `src/application/handlers`. No command bus |
| Factory Method           | The `@staticmethod` named factories on a class (`Result.success()`, `AssignmentKind.from_options(options=...)`), returning a new instance of that class                                                                                                                                                                                                    |
| Strategy / Specification | `src/application/domain/models`. A domain algorithm behind a small `ABC` with one `@final` class per variant, or a business-named predicate on the model (`is_`, `has_`, `belongs_to`). A rule `Issue` and `PullRequest` share lives once in a value object under `models/commons/`                                                                        |
| State                    | `src/application/domain/models`. A status `StrEnum` (`<model>_status.py`) with predicate and transition methods, behavior that varies per member as a method on the enum                                                                                                                                                                                   |
| Decorator / Proxy        | `src/driven/`. A `@final` class implementing the same outbound port `ABC` it wraps (cache, retry, log, access guard), without editing the wrapped adapter, wired in `src/dependencies.py`                                                                                                                                                                  |
| Observer                 | No standing home. The action runs one use case per invocation and the handler calls each outbound port directly. No observer registry, no event bus                                                                                                                                                                                                        |
| Chain of Responsibility  | No standing home, the action has no middleware stack. Only a genuine pass-along pipeline (successive checks, each able to short-circuit) would justify it, inside the one layer that owns the checks                                                                                                                                                       |
| Builder                  | Tests only. A test data builder under `tests/support/builders/` per `rules/python-testing.md` and `python-writing-tests`, the one place the `Builder` suffix and defaults are legitimate. Production uses the dataclass constructor and named factories                                                                                                    |

- **Naming**: no pattern-name suffix, the class keeps its business name. Owned by `rules/python-code-style.md`
  § Naming.
- **Command and handler pair**: the console driver builds the command and calls the inbound port, never the
  concrete handler. A handler never invokes another handler or inbound port, so
  `PullRequestsAndIssuesAssigningHandler` depends on the outbound ports directly. There is no generic
  `handle(command: Command)` port: the commands share fields through `AssignmentCommand`, but each inbound port is
  typed on its own `@final` command. Owned by `rules/python-architecture.md` § Commands and handlers.
- **Escalation thresholds (start simple)**: a status `StrEnum` before per-state classes (State), a `match` or
  dispatch `dict` kept inside its owner before it is lifted to a Strategy `ABC`, a combinator only on the third
  real composition (Specification). The detail is in `references/catalog.md`.

## Catalog

`references/catalog.md` carries every pattern's intent, structure, a generic minimal Python example, the
trade-off that bounds it, and its this-action note. There is no generator for a pattern. Read the catalog entry
before writing the class, then write it in the home § In this action names for it.

## Sources

- Gamma, Helm, Johnson, Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (1994).
- Refactoring Guru, "Design Patterns".
- The naming invariant and the dependency rules are this project's own, in `rules/python-code-style.md` and
  `rules/python-architecture.md`.
