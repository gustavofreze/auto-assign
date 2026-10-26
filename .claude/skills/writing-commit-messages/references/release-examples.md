# Release tag examples

Anchors for suggesting a tag. Each one names the range that was read, the tag that came out of it, and the bullets that
went with it.

## First release, nothing published yet

`git describe --tags --abbrev=0` finds no tag, so the range is the whole history.

```
1.0.0

- Add the order lifecycle, from creation through cancellation.
- Add the customer listing with keyset pagination.
- Publish the OpenAPI contract for both.
```

Say outright that the repository has no published tag and that this is the first one.

## Patch, only fixes and maintenance in the range

Last published tag `1.3.0`. Range `1.3.0..HEAD`, three commits, no `feat` and no breaking change.

```
1.3.1

- Update the GitHub Actions dependencies.
```

Two of the three commits were bot bumps and collapsed into one bullet. The third renamed an internal helper and earned
no bullet at all.

## Minor, one feature among the maintenance

Last published tag `1.3.1`. Range `1.3.1..HEAD`, eleven commits, one of them a `feat`.

```
1.4.0

- Add the order cancellation endpoint.
- Correct the confirmation window, which fired early against providers reporting minutes.
- Update the runtime image and the test dependencies.
```

Eleven commits, three bullets. The single `feat` decided the bump even though ten of the eleven were not features.

## Major, a breaking change in the range

Last published tag `1.4.0`. Range `1.4.0..HEAD` carries a commit with a `BREAKING CHANGE` footer.

```
2.0.0

- Replace the order status strings with an enumeration. A consumer reading the raw value has to map the old spellings.
- Add the bulk cancellation endpoint.
```

The breaking bullet goes first and says what the consumer has to do, because that is the only reason the major exists.

## Nothing user visible in the range

Last published tag `2.0.0`. Range `2.0.0..HEAD` is four commits of formatting and CI configuration.

```
2.0.1

- No user-visible change. Internal formatting and CI configuration only.
```

The filter emptied the list, so the range still takes a patch and the single bullet says as much outright.

## The spelling is copied, never chosen

The prefix comes from the last published tag and from nowhere else.

| Last published | Next patch | Next minor | Next major |
|----------------|------------|------------|------------|
| `1.3.0`        | `1.3.1`    | `1.4.0`    | `2.0.0`    |
| `v1.3.0`       | `v1.3.1`   | `v1.4.0`   | `v2.0.0`   |

A repository with no published tag has nothing to copy, so the first suggestion is a bare `1.0.0`. A repository whose
last tag is not semver at all (a date, a build number) is the one case to stop and ask, because there is no bump rule to
apply and guessing one silently changes how the project versions itself.
