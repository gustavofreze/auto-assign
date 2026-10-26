---
description: Design-principle residue only, the precedence ladder, the binding force (MUST vs SHOULD), and the admitted homes for shared code. The per-principle teaching lives in the python-applying-design-principles skill.
paths:
  - "src/**/*.py"
---

# Design principles (precedence, binding force, shared-code homes)

This rule keeps the precedence ladder, the binding force that gives the principles teeth, and the admitted homes for
shared code. The per-principle teaching (SOLID, DRY, Tell-Don't-Ask, complexity, decision routing) lives in the
`python-applying-design-principles` skill. A textbook formulation never overrides an existing rule, and any
disagreement is flagged rather than resolved silently. Refer to `rules/python-code-style.md` for the checklist applied
to all Python code and to `rules/python-architecture.md` for the dependency direction that DIP enforces.

## Binding force

| Force  | Applies to                                                                                                                                                                                         |
|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MUST   | Single responsibility, Open-closed, Liskov, Interface segregation, Dependency inversion, Tell-Don't-Ask, DRY, Precedence, and the Pre-output checklist below. A violation is a defect to fix before the change lands. |
| SHOULD | Complexity as a decision input, and Decision routing. They steer the choice between admissible designs. A deviation ships only with its reason recorded in the change summary.                     |

## Pre-output checklist

1. Duplicated business knowledge has exactly one owner. Structural similarity alone is never unified. See § DRY.
2. Shared code lives only in the homes § DRY admits. Never a new technical-role package. See § DRY.
3. When principles collide, § Precedence decides. Novel trade-offs are flagged, not resolved silently. See §
   Precedence.

## DRY

The DRY principle proper (knowledge over text, the wrong abstraction over premature duplication, the rule of three) is
in the `python-applying-design-principles` skill. Two structural lists stay here, tied to the hexagonal layout:

1. **Admitted homes for shared code**, and no others:
    - `src/application/domain/models/commons/`. Shared **domain knowledge** only: value objects reused by more than
      one model (an assignee list with its self-assignment rule, for example). No adapter or framework type lands
      here.
    - `src/driven/<technology>/`. Code shared among the modules of a **single** technology (the PyGithub-to-domain
      translation used by every GitHub adapter).
    - `src/driver/console/`. Cross-cutting **console** concerns shared by the driver (request parsing, exit codes,
      the action result).

   Creating a technical-role package (`src/utils`, `src/helpers`, `src/common`, `src/shared`) is prohibited. A generic
   name is the symptom. The missing owner is the disease.

2. **Duplication that is correct by design**, never to be unified:
    - Parallel driven adapters that satisfy different outbound ports over the same technology keep their own
      translation when the shapes differ. The resemblance between two adapters is never the trigger.
    - The parse-then-construct pair at the boundaries. The driven environment adapter parses raw inputs into
      primitives, the handler promotes the command primitives into value objects, and the value object constructor
      re-validates them. That is defense at the boundary plus the invariant in the constructor, not duplication to
      collapse.

## Precedence

When two principles point in opposite directions, the first applicable line wins:

1. Specification semantics over any rule (`CLAUDE.md` and the action contract in `action.yml` and `README.md`).
2. An existing rule in `.claude/rules/` over a textbook principle.
3. Context boundary over DRY: never share to avoid duplicating across the domain/adapter seam or across two
   technologies under `src/driven/`.
4. Explicit duplication over a wrong abstraction.
5. Composition over inheritance: small `ABC` ports and injected collaborators over a shared base class.
6. No preventive abstraction: a port, a helper, or a method exists only when a present consumer or a port boundary
   requires it. Methods are added on demand, never preventively.

When no line above resolves the collision, the trade-off is novel: choose the option that keeps the change reversible
and adds no preventive abstraction, record the decision in the change summary, and proceed without blocking on it.

## Delegated to owners

- Single responsibility, Open-closed, Liskov, Interface segregation, Tell-Don't-Ask, the general DRY principle,
  complexity as a decision input, and the decision-routing trees: the `python-applying-design-principles` skill.
- Dependency inversion as a dependency direction and its enforcement: `rules/python-architecture.md` and the
  `python-applying-hexagonal-architecture` skill.
