---
description: Naming, ordering, triggers, pinning, permissions, timeouts, and concurrency rules for GitHub Actions workflow files and the action manifest.
paths:
  - ".github/workflows/**/*.{yml,yaml}"
  - "action.yml"
---

# Workflows

Structural and stylistic rules for the workflow files under `.github/workflows/` and for `action.yml`. This
repository owns its workflows directly: there is no reusable workflow it calls out to, so every item applies to the
file in front of you.

## Pre-output checklist

Verify every item before producing any workflow YAML.

1. Each workflow has a single responsibility: `ci.yml` tests code, `codeql.yml` scans it, `auto-assign.yml`
   dogfoods the action, `release.yml` publishes the action image when a release is published. Never combine two.
2. `ci.yml` triggers on `pull_request` targeting `main` and on `workflow_dispatch`. No `push` trigger.
3. Top-level keys follow canonical order: `name`, `on`, `concurrency`, `permissions`, `env`, `jobs`.
4. Job-level keys follow canonical order: `if`, `name`, `needs`, `runs-on`, `environment`, `timeout-minutes`,
   `strategy`, `outputs`, `permissions`, `env`, `steps`.
5. Every other mapping (`with`, `env`, `outputs`, `permissions`, inputs) orders its keys by **name length
   ascending**, ties alphabetically, so `contents` precedes `id-token`.
6. CI jobs are independent and run in parallel: `review`, `test`, and `image` (the action image build). Each runs
   `make configure` before its own target.
7. Step names start with a verb in sentence case: `Checkout repository`, `Run review`, `Build action image`.
8. No Python version is hardcoded in a workflow. CI runs through the `Makefile`, so the interpreter is the one the
   tooling image tag pins, the same one a developer runs.
9. Top-level `permissions` default to read-only (`contents: read`). A job escalates only what it needs.
10. Every action, first-party (`actions/*`, `github/*`) and third-party alike, is pinned to a full commit SHA with
    the version as a trailing comment: `uses: actions/checkout@<sha> # v7`. Preserve the prefix style of the
    original pin when deriving the comment (`v2.1.0` becomes `v2`, `2.1.0` becomes `2`). Verify the latest release
    before pinning, and respect the dependency cooldown in `CLAUDE.md`.
11. No secret is hardcoded. Secrets reach a step through `secrets.*`, and the default `GITHUB_TOKEN` is preferred over
    a personal token.
12. A sensitive value read at runtime is masked with `::add-mask::` before it is assigned or echoed.
13. Every job sets `timeout-minutes`: 10 to 15 for CI jobs. Deviate only with a justifying comment.
14. `ci.yml` sets `concurrency` with a `group` scoped to the pull request and `cancel-in-progress: true`.
15. Inline `run:` logic longer than three lines is a `make` target or a composite action under `.github/actions/`.
    CI calls the same `make` target a developer runs, never a reimplementation of it.
16. All text (names, descriptions, comments) uses American English, and descriptions end with a period.

## Action manifest

`action.yml` is the public contract of this action, so it follows the same text rules and three more:

1. Every input has a `description` ending with a period and an explicit `required`.
2. Input names use `snake_case`, matching the `INPUT_<NAME>` variables the settings adapter reads.
3. A change to an input name, default, or meaning is a breaking change for consumers. It is documented in `README.md`
   in the same change and drives a major version bump (`writing-commit-messages` § Release tag).
4. `runs.image` points at the prebuilt image of the version being released (`docker://<registry>/<image>:<version>`).
   The release that publishes that version pushes the image through `make publish`, so the tag in `action.yml` is
   bumped in the same change that prepares the release.
