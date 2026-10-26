# Asserting exceptions

Three rules govern every failure test, and they compose:

1. **Assert the type, never the message.** `pytest.raises(X)` with the most specific class the code raises. The message
   is presentation, and `rules/python-testing.md` § Rules item 8 admits a message assertion only when the message
   itself is the action output.
2. **Drive the call path that raises.** Invoke the model, handler, driver, or adapter method that is supposed to fail.
   Never construct the exception and assert on its attributes, and never write a test module whose only job is to
   prove an exception class can be built.
3. **No `try` in a test body.** `pytest.raises` is the only way a test expects a failure (`rules/python-testing.md` §
   Rules item 4).

Message matching, constructing the exception to inspect it, and the `try` block smuggled into a test are the recurring
smells this reference exists to remove. The domain exception shape is owned by `rules/python-domain.md`, the placement
of each failure family by `rules/python-architecture.md` § Error placement.

## At a glance, pick the assertion by what the contract is

| The exception is                                          | Assert its                   | Shape                                                                                                |
|-----------------------------------------------------------|------------------------------|------------------------------------------------------------------------------------------------------|
| A domain exception signaling one invariant                | type                         | `with pytest.raises(AssigneesRequired):`                                                             |
| A domain exception carrying typed context                 | type, then context           | `with pytest.raises(X) as refusal:` then `refusal.value.<attribute>`                                 |
| An adapter exception translated from a `GithubException`  | type, then the chained cause | `with pytest.raises(GitHubRequestFailed) as request_failure:` then `request_failure.value.__cause__` |
| A message that is genuinely the action output             | text, sparingly              | `with pytest.raises(X, match='...'):`                                                                |

Never `pytest.raises(Exception)` or `pytest.raises(DomainException)` when a specific class is raised. The broad type
passes for the wrong failure.

## The Then before the When

The `# Then` names the failure and opens the `with pytest.raises(...)` block. The `# When` sits inside it, and is the
only statement there. Anything that follows the block runs after the failure was caught, so a complementary check is an
`# And` after the block.

```python
def test_assign_when_no_assignee_is_given_and_empty_assignment_is_denied_then_assignees_required_is_raised() -> None:
    # Given an issue without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # Then the assignment fails because no assignee was given
    with pytest.raises(AssigneesRequired):
        # When the issue is assigned to nobody while an empty assignment is denied
        issue.assign(
            assignment=AssignmentBuilder.new()
            .with_assignees(assignees=Logins.empty())
            .with_allow_no_assignees(allow_no_assignees=False)
            .build()
        )
```

## Reading carried context

A domain exception carries its context as typed attributes when a caller reads it (`rules/python-domain.md` § Domain
exceptions). None of this repository's exceptions does today: `SelfAssignmentNotAllowed`, `GitHubRequestFailed`, and
`MissingActionInput` fold their context into the message and expose no attribute. Once an exception gains an
attribute a caller reads, the test asserts it off `ExceptionInfo.value`, after the type was asserted. The name of the
captured `ExceptionInfo` says what failed (`refusal`, `request_failure`), never `exc`, `error`, or `e`. Until then the
test stops at the type:

```python
def test_assign_when_actor_assigns_itself_and_self_assignment_is_denied_then_it_is_refused() -> None:
    # Given an issue without assignees
    issue = Issue(number=1, author=Login(value='carol'), assignees=Logins.empty())

    # Then the assignment fails because the actor would assign itself
    with pytest.raises(SelfAssignmentNotAllowed):
        # When the actor assigns the issue to itself while self-assignment and an empty assignment are denied
        issue.assign(
            assignment=AssignmentBuilder.new()
            .with_actor(actor=Login(value='octocat'))
            .with_assignees(assignees=Logins.from_raw(values=('octocat',)))
            .with_allow_self_assign(allow_self_assign=False)
            .with_allow_no_assignees(allow_no_assignees=False)
            .build()
        )
```

## Asserting a translation and its cause

A driven adapter catches a `GithubException` and raises the typed exception its package owns, chained with
`raise ... from` (`rules/python-code-style.md` § Exceptions). The test drives the adapter against a `RepositorySpy`
that raises the `GithubException` on demand, asserts the adapter's type, and then asserts the chain. The chain is the
evidence that the cause was not swallowed.

```python
def test_assignable_when_github_fails_then_github_request_failed_is_raised() -> None:
    # Given a repository that fails any request
    assignees = GitHubAssignees(repository=RepositorySpy(records=(), members=(), failure=GithubException(status=500)))

    # Then the lookup fails with the translated failure instead of an empty selection
    with pytest.raises(GitHubRequestFailed) as request_failure:
        # When the assignable logins are requested
        assignees.assignable(logins=Logins.from_raw(values=('alice',)))

    # And the GitHub failure is chained as its cause
    assert isinstance(request_failure.value.__cause__, GithubException)
```

The opposite outcome is a defect the test must catch: an adapter that answers `()` when the lookup failed turns "the
call failed" into "nothing found" (`rules/python-architecture.md` § Error placement, rule 3).

## When `match=` is legitimate

Only when the text is the observable contract, which in this action means a message written to the action output.
Even then, match a stable, deliberately worded fragment with an anchored pattern, never the whole sentence copied from
the source. A domain exception message is a plain English sentence describing the invariant, and it is presentation:
a copy edit must not break a test.

## Drive the raising behavior, never construct the exception to inspect it

Constructing an exception and asserting on its attributes exercises **no production code**. It proves only that a class
stores its inputs.

```python
# Prohibited: the exception tested as a value, no behavior runs
def test_init_when_actor_is_given_then_the_message_names_the_actor() -> None:
    # When the exception is built
    refusal = SelfAssignmentNotAllowed(actor=Login(value='alice'))

    # Then its message names the actor
    assert str(refusal) == 'Not allowed to self-assign <alice>.'
```

The correct shape is the one in "Reading carried context" above: drive `issue.assign(assignment=...)` into the refusal
and assert the type of the raised instance.

Building an exception as the **stimulus** a `Spy` raises is a different thing and is allowed. In the console driver
test, `IssuesAssigningSpy(failure=AssigneesRequired())` hands the driver an exception of one family, and the assertion
is on the exit `Code` the driver produces, not on the exception.

## Coming from the Go and PHP shapes

| Elsewhere                                                | Here                                                                 |
|----------------------------------------------------------|----------------------------------------------------------------------|
| `expectException(X::class)`, `require.ErrorIs`           | `with pytest.raises(X):`                                             |
| try/catch plus accessors, `require.ErrorAs` plus getters | `with pytest.raises(X) as refusal:` then `refusal.value.<attribute>` |
| `getPrevious()`, walking the `%w` chain                  | `refusal.value.__cause__`                                            |
| `expectExceptionMessage('...')`, `require.ErrorContains` | `match='...'`, only when the text is the action output               |
| `new X(...)` then assert accessors                       | **delete it**, drive the path that raises `X`                        |

## Anti-patterns (reject on sight)

- `assert str(refusal.value) == '...'` or `'...' in str(refusal.value)` for text that is not the action output.
- `try:` and `except X:` in a test body, with a `pytest.fail(...)` after the call. Use `pytest.raises`.
- `pytest.raises(Exception)` or `pytest.raises(DomainException)` where a specific class is raised.
- Two statements inside the `with pytest.raises(...)` block. Only the `# When` call belongs there, otherwise the test
  passes when the setup line raises.
- An assertion inside the `with` block after the raising call. It never runs.
- A test module dedicated to one exception class, or an exception built only to read its attributes back.

## Decision order

1. **Does the caller branch on the exception class?** Assert the type with `pytest.raises(X)`.
2. **Does the caller read typed context off it?** Assert the type, then the attribute off `refusal.value` in an
   `# And` after the block.
3. **Is it a translation of a third-party failure?** Assert the adapter's type, then `__cause__`.
4. **Is the message genuinely the action output?** `match=` with a stable fragment, sparingly.

In every branch the exception is produced by driving the real behavior.
