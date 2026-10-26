# Commit message examples

Anchors for writing a new message. The subjects are deliberately ordinary, because what carries over is the shape and
not the domain.

## feat: single purpose, no body

```
feat: Add the order cancellation endpoint.
```

```
feat: Add pagination to the customer listing.
```

## fix: non-obvious cause, the body earns its place

```
fix: Correct the confirmation window in the routing rule.

The provider reports the window in minutes while the domain expects
seconds, so the rule fired early. Convert at the boundary and keep the
domain in seconds.
```

The body is there because nothing in the diff says the provider uses minutes. Without that sentence the next reader
derives it again from the provider documentation.

## fix: obvious cause, no body

```
fix: Reject a negative quantity on the order line.
```

## refactor: behavior preserving, no body

```
refactor: Extract the status transitions into the aggregate.
```

## test: coverage only, no body

```
test: Add a round-trip test for the order repository.
```

## chore: maintenance, no body

```
chore: Remove the unused order mapper.
```

## build: dependency change, no body

```
build: Upgrade the HTTP client to 2.3.
```

## A body that should never have been written

```
refactor: Extract the status transitions into the aggregate.

This commit extracts the status transitions into the aggregate. It
touches the order, the order status, and the order service. First the
method moved, then the call sites were updated, then the tests were
adjusted.
```

Three failures in one body. It restates the subject, it lists what the diff already lists, and it narrates steps nobody
will ever need. The subject on its own was the entire commit.

## Proposed split when the diff spans two intents

When a diff mixes a refactor and a feature, propose the split in this order:

```
refactor: Extract the assignee rules into a value object.
feat: Add the pull request reviewers adapter over its port.
```

The user decides whether to split or squash.
