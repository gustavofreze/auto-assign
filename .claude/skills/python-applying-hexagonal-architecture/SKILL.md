---
name: python-applying-hexagonal-architecture
description: Ports and adapters (hexagonal) architecture as a Python GitHub Action reference. Triggers on hexagonal architecture, ports and adapters, dependency rule, dependency inversion, DIP, inbound port, outbound port, command, handler, driving adapter, driven adapter, primary adapter, secondary adapter, console driver, composition root, dependency_injector container, anti-corruption layer, "where does this code go", "is this a port or an adapter", "inbound vs outbound", "should the driver call the handler", "does this belong in the handler or the model", Cockburn, Clean Architecture. Use when deciding which layer a piece of code belongs to, whether something is a port or an adapter, or which side of the hexagon it sits on.
---

# Hexagonal architecture (ports and adapters)

This skill is an opinionated synthesis of the ports and adapters pattern, distilled for a Python 3.14 GitHub Action
that assigns issues and pull requests. The architecture is universal and language-agnostic, so the concepts and the
short Python examples here use the action's own vocabulary (Issue, PullRequest, Assignee, Actor, Assignment). For the
canonical answer to any single question, follow the primary source named in § Sources (Cockburn for the shape, Martin
for the dependency direction). This is a teaching reference, not dogma, and not a restatement of the enforced rules.
Where a specific is enforced in this repository, § Where the enforced specifics live routes you to the rule that owns
it.

**One reframe up front.** The transport is the GitHub Actions runner, not HTTP. The action's inputs arrive as
environment variables, and the outcome leaves as an exit `Code` written to the action output. The console driver under
`src/driver/console/` is the driving adapter: it turns one run into one command and one inbound-port call, and it maps
whatever comes back to one exit code. Every use case owns its inbound port (an `ABC` with a single `handle(command)`),
its command (a frozen dataclass), and its handler (the one class that implements the port). There is no read side, so
no query handlers and no CQRS split. Every use case is a write that asks GitHub for the work and tells GitHub the
outcome.

## When to use (and when NOT to)

| Use when                                                         | Skip when                                                                   |
|------------------------------------------------------------------|-----------------------------------------------------------------------------|
| You are deciding which layer a module belongs to                 | The placement is obvious and already covered by a layer rule                |
| You cannot tell a port from an adapter, or inbound from outbound | You only need the literal folder shape (see `rules/python-architecture.md`) |
| A dependency seems to point the wrong way (outward)              | A tiny helper with no business rule and no swappable I/O                    |
| You want a technology to be swappable behind a contract          | The "technology" is the standard library, not an external dependency        |
| You are reviewing whether the core stays free of infrastructure  | The change touches only one adapter's internals, behind its port            |

**Start simple. Evolve complexity only when needed.** A port exists when a real use case or a real boundary requires
it, never preventively. A method on a port exists when a present handler calls it.

## The dependency rule (and the runnable-core test)

Source-code dependencies point inward only, and every handler must run with every outbound port replaced by a
hand-written `Spy` (no GitHub, no token, no network). The full rule, the runnable-core test, and the inversion
mechanism, each with a Python example, live in `references/ports-and-adapters.md` § The dependency rule and § The
runnable-core test.

## Concept boundaries

| Block                     | Primary question                               | Use it for                                                                                | Do not treat as                                                           |
|---------------------------|------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| Domain                    | What is always true, regardless of technology? | Models, value objects, enums, domain exceptions                                           | A place for PyGithub, `os.environ`, or `dependency_injector`              |
| Command                   | What exactly is the outside asking for?        | A frozen dataclass naming one use-case intent in primitives (`AssignIssues`)              | A request object carrying raw transport shapes                            |
| Inbound port              | How does the outside ask the core to act?      | One `ABC` per use case with a single `handle(command) -> None`                            | A generic `handle(command: Command)` shared by every use case             |
| Handler                   | What does the system do, step by step?         | Implementing one inbound port, orchestrating models and outbound ports                    | A home for business rules (those belong to the domain)                    |
| Outbound port             | What does the core need from the outside?      | The `ABC` a driven adapter implements, stated in domain types (`Issues`, `Assignees`)     | A PyGithub `Repository`, a `PaginatedList`, or a leaked `GithubException` |
| Driving adapter (console) | How does the runner reach the core?            | Reading the request, building the command, calling the inbound port, returning the `Code` | The place to make a domain decision                                       |
| Driven adapter            | How is a need actually fulfilled?              | `GitHubIssues`, `GitHubPullRequests`, `GitHubAssignees`, `ActionSettings`                 | A concrete type a handler or the driver imports                           |
| Composition root          | Where are the wires soldered?                  | `src/dependencies.py` declaring providers, `src/main.py` running the driver               | A home for business logic, validation, or a guard that raises             |

## Decision trees

### Where does this code go (domain vs application vs adapter)?

```
Does the code express a business rule or an invariant?
├─ YES → Does it touch I/O (GitHub, the environment, the filesystem, the clock)?
│        ├─ NO  → DOMAIN (a model or value object in src/application/domain/models,
│        │        a violation in src/application/domain/exceptions)
│        └─ YES → It is not pure domain. Split it:
│                 the rule → DOMAIN
│                 the I/O  → DRIVEN ADAPTER, behind an outbound port
└─ NO  → Does it orchestrate one use case (ask a port, tell a model, hand the outcome to a port)?
         ├─ YES → APPLICATION (a handler in src/application/handlers, behind an inbound port,
         │        taking a command from src/application/commands)
         └─ NO  → Does it speak a concrete technology (PyGithub, os.environ, the action output file)?
                  ├─ YES → ADAPTER (src/driver/console if it receives the run,
                  │        src/driven/<technology> if it fulfills a need)
                  └─ NO  → It is a contract the core owns. A PORT
                           (an ABC in src/application/ports/inbound or src/application/ports/outbound)
```

### Is this a port or an adapter?

```
Is it an ABC the core owns and the core depends on?
├─ YES → PORT (lives in src/application/ports)
│        It names a capability in domain terms, with no transport words.
│        Its docstrings state the contract. No concrete class carries one.
└─ NO  → Is it a concrete @final class that speaks one specific technology?
         ├─ YES → ADAPTER (lives outside the core)
         └─ NO  → Neither. A pure rule is DOMAIN, a use case is a HANDLER.
```

### Is this port inbound or outbound?

```
Which way does control cross this port?
├─ The outside DRIVES the core through it
│   (the runner starts the action, the console driver builds a command)
│   └─ INBOUND port (driving, primary)
│      Lives in src/application/ports/inbound, one per use case, typed on its own command.
│      Implemented BY the core (exactly one handler implements it).
└─ The core DRIVES the outside through it
    (a handler needs the open issues, the repository assignees, a saved assignment)
    └─ OUTBOUND port (driven, secondary)
       Lives in src/application/ports/outbound, in domain terms.
       Implemented OUTSIDE the core by a driven adapter, explicitly: class GitHubIssues(Issues).
```

### Is this adapter a driver or a driven?

```
Which side of the hexagon does the adapter sit on?
├─ It RECEIVES the run and then calls an inbound port
│   (the console driver under src/driver/console)
│   └─ DRIVING adapter (primary, the inbound side)
│      Depends on inbound ports, commands, and domain exceptions.
│      Never on a concrete handler, never on a driven adapter.
└─ It IMPLEMENTS an outbound port and speaks a technology
    (GitHubIssues, GitHubPullRequests, GitHubAssignees under src/driven/github)
    └─ DRIVEN adapter (secondary, the outbound side)
       Implements one outbound port. Owns the transport and translates its failures.
       ActionSettings under src/driven/environment is driven too, but only the root consumes it,
       so it implements no port.
```

## Generic structure

The concrete layout for this repository is owned by `rules/python-architecture.md`. Treat the tree below as the idea
mapped onto the real folders.

```
src/
├── application/                    # the application core (zero outward dependencies)
│   ├── domain/
│   │   ├── models/                 # models, value objects, StrEnum / IntEnum enums
│   │   │   └── commons/            # value objects shared by more than one model
│   │   └── exceptions/             # DomainException and one module per invariant violation
│   ├── commands/                   # frozen dataclasses, one per use-case intent (AssignIssues), on AssignmentCommand
│   ├── ports/
│   │   ├── inbound/                # one ABC per use case, a single handle(command) -> None
│   │   └── outbound/               # what the core needs: Issues, PullRequests, Assignees
│   ├── handlers/                   # <InboundPort>Handler, each implements exactly one inbound port
│   └── requested_assignment.py     # RequestedAssignment: command primitives to an Assignment, built by each
│                                   # handler (at the root, because a handler never imports from handlers/)
├── driver/                         # primary / driving adapter (calls inbound ports)
│   ├── console/                    # request in, one Assigner per kind builds the command, exit Code out,
│   │                               # AnnotationFormatter for the workflow annotations
│   └── exceptions/                 # invalid action configuration
├── driven/                         # secondary / driven adapters (implement outbound ports)
│   ├── github/                     # GitHubIssues, GitHubPullRequests, GitHubAssignees, GitHubRequestFailed,
│   │                               # GitHubIssueRecords and GitHubPullRequestRecords (the records in scope),
│   │                               # AssignmentJournal and JournalEntry (what the run assigned)
│   └── environment/                # ActionSettings: the action inputs, read once, as typed values,
│                                   # ActionOutput: the action outputs and step summary, written once
├── dependencies.py                 # composition root: a declarative dependency_injector container
└── main.py                         # entry point: read the settings, run the driver, write outputs and summary
```

The inbound and outbound port shapes, the command and the handler that implements the port, the driver and driven
adapters around them, and the composition root that wires them are in `references/ports-and-adapters.md`. The shapes
in this tree: the inbound port `IssuesAssigning` taking the command `AssignIssues`, the handler `IssuesAssigningHandler`
consuming the outbound ports `Issues` and `Assignees`, the driven adapters `GitHubIssues` and `GitHubAssignees` behind
them, and the console driver that calls `IssuesAssigning` without knowing which class answers.

## Building blocks

| Building block        | Role                                                         | Lives in                                           |
|-----------------------|--------------------------------------------------------------|----------------------------------------------------|
| Model                 | Identity plus the invariants of its boundary                 | Domain (src/application/domain/models)             |
| Value object          | An immutable value and the rules that bind it                | Domain (src/application/domain/models)             |
| Domain enum           | A `StrEnum` or `IntEnum` with a `from_raw` static factory    | Domain (src/application/domain/models)             |
| Domain exception      | One invariant violation, extending `DomainException`         | Domain (src/application/domain/exceptions)         |
| Command               | The typed input to one use case                              | Application (src/application/commands)             |
| Inbound port (`ABC`)  | The entry contract for one use case, a single `handle`       | Application (src/application/ports/inbound)        |
| Handler               | Implements one inbound port, orchestrates domain and ports   | Application (src/application/handlers)             |
| Outbound port (`ABC`) | A capability the core needs, in domain terms                 | Application (src/application/ports/outbound)       |
| Driving adapter       | Receives the run, builds the command, calls the inbound port | Driver (src/driver/console)                        |
| Driven adapter        | Implements an outbound port, owns the transport              | Driven (src/driven/github, src/driven/environment) |
| Composition root      | Wires concrete adapters and handlers to the ports            | src/dependencies.py and src/main.py                |

## Anti-patterns

| Anti-pattern                                                                               | Problem                                                                                                         | Fix                                                                                                            |
|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Domain imports infrastructure (PyGithub, `os.environ`, `dependency_injector`)              | The core can no longer run without that technology, the dependency rule is broken, the runnable-core test fails | Declare an outbound port in `ports/outbound`, move the technology into a driven adapter behind it              |
| The console driver calls an outbound port or PyGithub directly                             | The use case has no home, orchestration and transport tangle, the core cannot run without GitHub                | Route the driver through an inbound port to a handler, let the handler call the outbound port                  |
| The driver depends on a concrete handler (`IssuesAssigningHandler`)                        | The caller is welded to one implementation, swapping or doubling it means editing the caller                    | Depend on the inbound port (`IssuesAssigning`), let `src/dependencies.py` inject the handler                   |
| A handler invokes another handler or inbound port                                          | Use cases chain into each other, shared lookups run twice, and one test inherits the wiring of another          | Depend on the outbound ports directly. A rule two use cases share lives on a model or value object             |
| One generic `CommandHandler` port with `handle(command: Command)` shared by every use case | Every handler narrows the parameter type, a Liskov violation, and the port names no use case                    | One inbound port per use case, typed on its own command                                                        |
| An outbound port exposes PyGithub types (takes a `Repository`, returns a `PaginatedList`)  | The technology leaks through the contract, the inversion is only cosmetic                                       | Express the port in domain models, value objects, and builtins. Translate inside the adapter                   |
| A driven adapter catches `GithubException` and returns an empty tuple                      | A failed call reads as "nothing to assign", the action reports success on an outage                             | Raise a typed exception the adapter package owns, chained with `raise ... from`                                |
| A driven adapter holds a business rule (the self-assignment check inside `GitHubIssues`)   | The rule hides outside the domain, two adapters drift, the knowledge has no single owner                        | Move the rule onto the owning model or a value object in `models/commons`. Leave the adapter to translate only |
| A handler asks "is it already assigned?" before assigning                                  | A race between the check and the write, and a domain verb leaks into the orchestrator                           | Issue the operation and let the driven adapter report the outcome or translate the conflict                    |
| Settings read at import time (a module-level `os.environ` lookup)                          | Every import becomes a side effect, the core cannot be imported in a test without a full environment            | `ActionSettings` reads the inputs once, `src/main.py` hands the typed values to the container                  |
| A driven class named `Adapter`, imported with an alias to dodge the clash                  | The name says nothing (every repository, gateway, and client is an adapter), and the alias hides the defect     | Name it technology plus capability (`GitHubIssues`), module `github_issues.py`, one port per adapter           |
| Anemic core, behavior scattered across handlers and adapters                               | The "domain" is data bags, real logic lives in the outer layers                                                 | Push behavior inward. Tell the model to act rather than asking for its state                                   |
| The composition root validates input or raises                                             | Wiring and policy tangle, the guard has no owner and no test                                                    | Keep the root declarative. A precondition belongs to the concrete class it protects                            |

## Implementation order

1. Model the domain first: frozen dataclasses, enums, and domain exceptions. No I/O at all.
2. Name the use case: a command in `src/application/commands` and its inbound port in `src/application/ports/inbound`,
   with one abstract `handle(self, command: X) -> None`.
3. Discover the outbound ports the use case needs (the open issues, the repository assignees, a saved assignment) and
   declare them in `src/application/ports/outbound` in domain terms, with reST docstrings on the `ABC` and on each
   abstract method.
4. Write the `<InboundPort>Handler` that implements the inbound port, promotes the command primitives into value
   objects (through `RequestedAssignment` at the `src/application/` root when every handler shares the step), tells
   the domain models to act, and hands the outcome to the outbound ports.
5. Implement the driven adapters behind the outbound ports in `src/driven/github`, with the anti-corruption
   translation at the boundary and every `GithubException` re-raised as a typed exception. PyGithub types stay inside
   the package.
6. Implement the console driver that builds the command from the request, calls the inbound port, and maps each
   exception family to one exit `Code`.
7. Wire everything in `src/dependencies.py` as declarative `dependency_injector` providers, and let
   `src/main.py` read `ActionSettings` once, run the driver, and write the action outputs and step summary through
   `ActionOutput`.
8. Verify the dependency rule: every handler runs under pytest with each outbound port replaced by a hand-written
   `Spy` (no GitHub, no token, no network), and `make review` (pylint and `mypy --strict`) reports clean.

## Where the enforced specifics live

The concepts above are universal. Their enforced specifics in this repository live in the rules, which this skill does
not restate:

- **The layer contract, the inward-only import direction, the command and handler pair, error placement, the driven
  adapter naming, and the composition root** are owned by `rules/python-architecture.md`. Read it before creating any
  module under `src/`.
- **Domain building blocks** (models, value objects, enums, domain exceptions, the import whitelist) are owned by
  `rules/python-domain.md`. Read it before modeling any type under `src/application/domain/`.
- **Typing, `@final`, frozen dataclasses, docstrings on ports only, keyword arguments, and imports** are owned by
  `rules/python-code-style.md`.
- **The Dependency Inversion Principle** as operationalized here (concrete outer-layer types never cross inward, the
  precedence ladder, the admitted homes for shared code) is owned by `rules/python-design-principles.md`. Apply it with
  the `python-applying-design-principles` skill.
- **When a placement calls for a specific pattern** (a dispatch `dict` instead of `elif`, a strategy behind a port, an
  anti-corruption translator, a configuration-driven selection at the root), reach for the
  `python-applying-design-patterns` skill.
- **Testing the runnable core with doubles** (Given/When/Then, one `# When`, hand-written `Spy` classes under
  `tests/support/spies/`, 100% branch coverage) is owned by `rules/python-testing.md`. Apply it with the
  `python-writing-tests` skill.

## Reference documentation

| Topic                                                                                                                                                                                                   | File                               |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| The dependency rule, the runnable-core test, the inbound and outbound port taxonomy, the driver and driven adapters, the composition root, and the anti-corruption boundary, each with a Python example | `references/ports-and-adapters.md` |

## Sources

- Cockburn, Alistair. "Hexagonal Architecture" (2005). The original statement of ports and adapters.
- Martin, Robert C. "The Clean Architecture" (2012), The Clean Code Blog.
- Martin, Robert C. "Clean Architecture: A Craftsman's Guide to Software Structure and Design", Prentice Hall (2017).
- Martin, Robert C. "The Dependency Inversion Principle", C++ Report (1996). The inversion that makes the outbound port
  point inward.
