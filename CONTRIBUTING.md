# Contributing

* [Overview](#overview)
* [How can I contribute?](#contributing)
    - [Reporting bugs](#reporting-bugs)
    - [Suggesting improvements](#suggesting-improvements)
    - [Developing](#developing)

<div id='overview'></div> 

## Overview

Thank you for investing your time in contributing to the project.

These are the main guidelines, use your common sense, and feel free to propose changes to this document in a pull
request.

<div id='contributing'></div> 

## How can I contribute?

This section guides you through possible ways to contribute.

<div id='reporting-bugs'></div> 

### Reporting bugs

Bugs are tracked as [issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) on
GitHub, then in the respective repository the bug is related to, create an issue, and provide the following information:

- Use a clear and descriptive title to identify the problem.
- Describe the exact steps that reproduce the problem in as much detail as possible. When listing the steps, don't say
  just what you did, but explain how you did it.
- Tell, which version of the package you are using.

<div id='suggesting-improvements'></div> 

### Suggesting improvements

Improvement suggestions are tracked
like [issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) in
GitHub, then in the respective repository that your improvement suggestion is related to, create an issue, and provide
the following information:

- Use a clear and descriptive title to identify the suggestion.
- Describe current behavior, and explain what behavior you expected to see and why.
- Explain why this enhancement would be useful for most users
- Tell, which version of the package you are using.

<div id='developing'></div> 

### Developing

To start development, you will need to follow a few steps:

- Fork the repository in which you intend to develop.

- Make a clone of the repository from your fork.

- Create a new branch from the **main** branch. To give greater readability, use one of the prefixes, according to the
  implementation type, **bug-fix**/xpto, **feature**/xpto, **release**/tag.

- Make the commits following [Conventional Commits](https://www.conventionalcommits.org), with no scope, in the form
  `<type>: <Description>.`, where the description is in English, in the imperative mood, capitalized, and ends with a
  period. One logical change per commit.

    - **feat**: adds new behavior visible to the action's users.
        - e.g. (feat: Assign only the item that triggered the event.)

    - **fix**: corrects wrong behavior.
        - e.g. (fix: Leave the actor out when self-assignment is denied.)

    - **refactor**: restructures code with no behavior change.
        - e.g. (refactor: Extract the self-assignment rule into a value object.)

    - **test**: adds or adjusts tests only.
        - e.g. (test: Cover the event-scoped listing of pull requests.)

    - **docs**: changes documentation only.
        - e.g. (docs: Document which items are assigned per event.)

    - **build**: changes dependencies, the Dockerfile, or the Makefile.
        - e.g. (build: Upgrade PyGithub to 2.10.)

    - **ci**: changes the GitHub Actions workflows.
        - e.g. (ci: Pin every action to a full commit SHA.)

    - **chore**: housekeeping that fits no other type.
        - e.g. (chore: Remove the unused issue mapper.)

    - **revert**: undoes a previous commit.
        - e.g. (revert: Revert "feat: Assign only the item that triggered the event.")

- Before opening a pull request, run `make review` and `make test`. Both must pass.

- To exercise the action against the real GitHub API without publishing anything, run `make smoke`. It builds the
  same image the runner builds and runs it with the environment the runner injects, against a sandbox repository you
  own. Put a fine-grained token scoped to that repository in a git-ignored `.env.local`, as
  `INPUT_GITHUB_TOKEN=<token>`. Then pick the simulated event:
    - e.g. (`make smoke REPOSITORY=owner/sandbox ACTOR=login EVENT=issue NUMBER=1`)
    - e.g. (`make smoke REPOSITORY=owner/sandbox ACTOR=login EVENT=pull_request NUMBER=2 OPTIONS=PULL_REQUEST`)
    - e.g. (`make smoke REPOSITORY=owner/sandbox ACTOR=login EVENT=scan OPTIONS=ISSUE,PULL_REQUEST`)

  `ASSIGNEES` defaults to `ACTOR`. `ALLOW_SELF_ASSIGN`, `ALLOW_NO_ASSIGNEES`, `ASSIGN_AUTHOR`, `SKIP_BOTS`, and
  `SKIP_DRAFTS` take `true` or `false`. The printed lines are what the action writes to `GITHUB_OUTPUT`, followed by
  the step summary.

- Once the tests and the automated code review pass, create a new branch from the **main** branch, using the prefix
  **release/tag**. Then open a pull request from your branch to the **release/tag** branch.

- With the code review approved, merge the **release/tag** branch to the **main** branch. Create a new tag following
  o [semantic versioning](https://semver.org), and for the release, adding the prefix **v** + **tag**.
    - e.g (tag: **1.0.0**)
    - e.g (release: **v1.0.0**)

- The action runs a prebuilt image, so the release branch also sets `runs.image` in `action.yml` to the tag being
  released (`docker://ghcr.io/gustavofreze/auto-assign:<tag>`). Publishing the release triggers `release.yml`, which
  pushes that image through `make publish`. The first time, set the `auto-assign` package visibility to **public** in
  the GitHub package settings, so consumers can pull it.
