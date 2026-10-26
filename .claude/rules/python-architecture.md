---
description: The hexagonal layer contract for this Python service, the inward-only dependency rule, the driver/application/ports/domain/driven mapping, command and handler shape, error placement, driven-adapter conventions, and the composition root.
paths:
  - "src/**/*.py"
---

# Hexagonal architecture (ports and adapters)

This rule owns the structural contract of the hexagon: the inward-only dependency rule, the layer mapping onto this
repository, the command and handler pair, where a failure class lives, how driven adapters are named and bounded, and
what the composition root may and may not do. Domain building blocks are owned by `rules/python-domain.md`. Naming,
typing, and exception mechanics are owned by `rules/python-code-style.md`. SOLID and pattern selection are owned
elsewhere. See § Delegated to owners.

## Pre-output checklist

Verify every item before producing or relocating any module under `src/`.

1. Dependencies point inward only: `driver` to `application` (ports, commands) to `domain`, and `driven` implements
   `application/ports/outbound`. `domain` imports nothing outward. See § Dependency rule.
2. The driver depends on inbound port types and commands, never on a concrete handler or a driven adapter. A handler
   depends on outbound ports and the `src/application/` root collaborators only, never on a concrete driven adapter,
   another handler, or an inbound port. See § Commands and handlers.
3. A failure class lands in the right place: invariant violations in the domain. Not-found, conflict, policy, and
   transport failures outside it. See § Error placement.
4. The driver carries zero business rules, and no handler pre-checks existence or uniqueness before a mutating call.
   See § Thin driving side.
5. Every driven adapter is named by technology plus capability (never a bare `Adapter`), implements one outbound
   port, and translates third-party failures into typed exceptions at its boundary. No PyGithub type crosses a port.
   See § Driven adapter conventions.
6. `src/dependencies.py` and `src/main.py` are declarative wiring only. See § Composition root.

## Dependency rule

```
src/main.py + src/dependencies.py   (composition root, the only place that names every concrete)
    │ constructs and injects concretes
    ▼
src/driver/console ──calls──▶ application/ports/inbound ◀── implemented by ── application/handlers
   (driving adapter)              │                                                │ depend on
                                  ▼                                                ▼
                          application/commands                     application/ports/outbound
                                                                           ▲ implemented by
                                                                           │
                                                                    src/driven/<technology>
    all of the above depend on ▼
src/application/domain   (models, exceptions, imports nothing outward)
```

1. `driver` depends on `application/ports/inbound`, `application/commands`, and `application/domain/exceptions`.
2. `application/handlers` implement inbound ports and depend on outbound ports, the domain, and the application
   collaborators at the `src/application/` root (`requested_assignment.py`).
3. `driven` implements the `ABC`s in `application/ports/outbound`, explicitly (`class GitHubIssues(Issues)`).
4. `domain` knows nothing of `driver`, `driven`, `dependencies`, ports, commands, handlers, or any framework.

No module under `application` or `driver` ever constructs a concrete adapter or handler. The composition root does
that and injects the abstraction.

## Layer contract

| Layer                        | Directory                                  | Role                                                                                                               | May import                                                                                       |
|:-----------------------------|:-------------------------------------------|:-------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|
| **Driver** (driving adapter) | `src/driver/console`                       | Reads the action inputs into a request, builds a command, calls the inbound port, maps the outcome to an exit code | `application.ports.inbound`, `application.commands`, `application.domain.exceptions`, `driver.*` |
| **Commands**                 | `src/application/commands`                 | Frozen dataclasses naming one use-case intent in primitives                                                        | stdlib only                                                                                      |
| **Handlers**                 | `src/application/handlers`                 | Implement an inbound port, orchestrate domain models and outbound ports                                            | `ports`, `commands`, `domain`, `application` root collaborators                                  |
| **Collaborators**            | `src/application/*.py`                     | Application steps every handler shares (`RequestedAssignment` turns a command into an `Assignment`)                | `ports.outbound`, `commands`, `domain`                                                           |
| **Ports**                    | `src/application/ports/{inbound,outbound}` | `ABC` contracts. Inbound: one `handle(command)` per use case. Outbound: what the core needs from the outside       | `commands`, `domain`                                                                             |
| **Domain**                   | `src/application/domain`                   | Models, value objects, enums, domain exceptions                                                                    | stdlib + `domain` only                                                                           |
| **Driven** (driven adapters) | `src/driven/<technology>`                  | Implement outbound ports over GitHub, the environment, the filesystem                                              | `ports.outbound`, `domain`, stdlib, third party                                                  |
| **Composition root**         | `src/dependencies.py`, `src/main.py`       | Builds the object graph and runs the driver                                                                        | everything                                                                                       |

## Commands and handlers

1. A command is a `@final` frozen dataclass in `src/application/commands/`, named as an imperative intent
   (`AssignIssues`). It carries primitives only (builtins and tuples of builtins), never a domain type and never a raw
   transport shape. Commands that share their fields extend one non-final base (`AssignmentCommand`), and each
   use-case command stays an empty `@final` subclass. The handler promotes the primitives into value objects
   (`Login(value=command.actor)`) through `RequestedAssignment`.
2. An inbound port is an `ABC` in `src/application/ports/inbound/` with one abstract `handle(self, command: X) ->
   None`, named as the subject followed by the gerund (`IssuesAssigning` for the command `AssignIssues`, module
   `issues_assigning.py`). One port per use case, typed on its own command. A generic `handle(command: Command)` port
   shared by every use case is a Liskov violation.
3. A handler is a `@final` class in `src/application/handlers/` named `<InboundPort>Handler`
   (`IssuesAssigningHandler`), implementing exactly one inbound port.
4. A handler never invokes another handler or inbound port, and the driver never sequences two inbound ports for one
   invocation. A use case that spans two kinds of item talks to their outbound ports directly. Shared logic is a
   method on a domain model or value object, never a second handler.
5. A handler tells domain models to act and hands the outcome to outbound ports. It holds no business rule a model
   could own.
6. An application step every handler repeats lives in a `@final` collaborator at the `src/application/` root, never
   under `handlers/`, because a handler never imports from `src.application.handlers`. `RequestedAssignment`
   (`requested_assignment.py`) promotes a command's primitives into `Login`, `Logins`, and `Eligibility`, asks the
   `Assignees` port which logins the repository accepts, and returns the `Assignment`. Each handler builds one in its
   constructor from the injected `Assignees` port and calls `from_command(command=...)` after its early return. It is
   not a port and is never wired in the composition root.

## Boundary naming

Subdirectory names under `src/driven/` name the **external system or technology** the adapter fronts (`github`,
`environment`). Subdirectory names under `domain/models/` name a bounded concept. Neither ever encodes visibility
(`internal`, `public`), audience (`admin`, `web`), technical role (`sync`, `batch`), or layering (`service`,
`manager`, `handler`). Foreign concepts (a PyGithub `Issue`, a `NamedUser`) are translated into domain terms at the
driven boundary, the anti-corruption layer.

## Error placement

| Failure                                                                                 | Kind       | Home                                                       |
|:----------------------------------------------------------------------------------------|:-----------|:-----------------------------------------------------------|
| Format, membership, required-field, range, state violation a model enforces on itself   | **Domain** | `src/application/domain/exceptions`                        |
| Not-found (a lookup miss)                                                               | Not domain | outside `domain`, returned as an absence or raised by the adapter |
| Conflict, idempotency, already-assigned                                                 | Not domain | the driven adapter that observes it                        |
| Invalid action configuration (an unknown assignment option, a missing input)            | Not domain | `src/driver/exceptions` or `src/driven/environment`        |
| GitHub API, network, authentication, or rate-limit failure                              | Not domain | a typed exception owned by `src/driven/github`             |

Rules:

1. **Domain exceptions are pure.** See `rules/python-domain.md` § Domain exceptions.
2. **Not-found is never a domain exception.**
3. **Infrastructure failures stay in `driven`.** A `GithubException` is caught inside the adapter and re-raised as a
   typed exception the adapter package owns, chained with `from`. It is never swallowed into an empty result: an
   empty list means "nothing found", never "the call failed".
4. **The driver maps, once.** The console driver maps each exception family to one exit `Code`. Nothing below it
   knows about exit codes.

## Thin driving side

The console driver translates one action invocation into one command and one inbound-port call. It holds **no
business rules**. A driver that computes a business value or re-derives a value object the domain already builds has
absorbed logic that does not belong to it.

**Never pre-check existence or uniqueness before a mutating call.** Asking "is this already assigned?" and then
deciding whether to act has two defects: a TOCTOU race between the check and the write, and a domain verb leaking into
the orchestrator. Issue the operation and let the driven adapter report the outcome or translate the conflict.

## Driven adapter conventions

| Responsibility             | Outbound port      | Driven class (technology prefix) | Location                 |
|:---------------------------|:-------------------|:---------------------------------|:-------------------------|
| Issues awaiting assignment | `Issues`           | `GitHubIssues`                   | `src/driven/github`      |
| Pull requests              | `PullRequests`     | `GitHubPullRequests`             | `src/driven/github`      |
| Repository assignees       | `Assignees`        | `GitHubAssignees`                | `src/driven/github`      |
| Issues in the run's scope  | (collaborator)     | `GitHubIssueRecords`             | `src/driven/github`      |
| Pull requests in scope     | (collaborator)     | `GitHubPullRequestRecords`       | `src/driven/github`      |
| Assignments of the run     | (collaborator)     | `AssignmentJournal`              | `src/driven/github`      |
| Action inputs              | (composition root) | `ActionSettings`                 | `src/driven/environment` |
| Action outputs and summary | (composition root) | `ActionOutput`                   | `src/driven/environment` |

A collaborator class serves the adapters of its own technology and never crosses a port. The records collaborators
hand PyGithub records to their adapter, which translates them. `AssignmentJournal` is shared by `GitHubIssues` and
`GitHubPullRequests`, which record a `JournalEntry` after each assignment, and `src/main.py` reads it back to write
the action outputs and step summary through `ActionOutput`.

1. **Name = technology prefix + port capability.** The module is `snake_case` after the class
   (`github_issues.py`). The bare name `Adapter` is prohibited: a repository, a gateway, and a client are all
   adapters, so the name says nothing.
2. **One port per adapter.**
3. **Translate at the boundary.** PyGithub objects, `PaginatedList`, and `GithubException` never escape the package.
4. **Port signatures speak domain.** Domain models, value objects, and builtins only.

## Composition root

`src/dependencies.py` is the single composition root, and `src/main.py` the process entry point that reads the
settings, builds the `AssignmentJournal` it hands to the container as a `providers.Dependency`, runs the driver, and
writes the action outputs and step summary through `ActionOutput`.

1. **Declarative wiring only.** No business logic, no validation, no guard that raises. A precondition belongs to the
   concrete class it protects.
2. **Wiring-only selection is allowed.** Choosing a concrete by configuration is a wiring decision.
3. **Constructor injection everywhere.** The `dependency_injector` container declares providers. No module outside
   `src/dependencies.py` imports the container or reads environment variables directly.
4. Settings are read once, by the driven environment adapter, and handed to the root as typed values. Module-level
   reads of `os.environ` at import time are prohibited, because they make every import a side effect.

## Delegated to owners

- Value objects, immutability, enums, ubiquitous-language naming, the domain import whitelist, and the domain
  exception shape: `rules/python-domain.md`.
- Typing, naming, docstrings, exception mechanics, and imports: `rules/python-code-style.md`.
- SOLID, DRY, precedence, and shared-code homes: `rules/python-design-principles.md`.
- The ports-and-adapters teaching and worked examples: the `python-applying-hexagonal-architecture` skill.
