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

- Make the commits using the following convention:

    - **fix**: is used when there are code errors that are causing bugs.
        - e.g (fix: Correct calculation [...])

    - **doc**: it is used when adding or modifying some documentation in the code, or the repository in question.
        - e.g (doc: Adds README.md [...])

    - **feat**: is used when adding some new functionality from scratch to the code.
        - e.g (feat: Adds validation [...])

    - **test**: is used when changes of any kind are made to the tests, whether it is the addition of new tests or
      refactoring of existing tests.
        - e.g (test: Adds unit test for [...])

    - **style**: is used when changes are made to the style and formatting of the code that will not impact any code
      logic.
        - e.g (style: Standardize code as [...])

    - **refactor**: it is used when a refactoring will not directly impact the code or any rules of
      business.
        - e.g (refactor: Optimize search [...])

  In the description use the imperative verb in the affirmative form., e.g. (**optimizes**, **adds**, **standardizes**,
  **adjusts**, **changes**).

- At the end of development, after you have run the tests and automated code reviews, so that it is
  Once the code review step is done, a new branch must be created from the **main** branch, using the prefix
  **release/tag**. Then open a pull request from your branch to the **release/tag** branch.

- With the code review approved, merge the **release/tag** branch to the **main** branch. Create a new tag following
  o [semantic versioning](https://semver.org), and for the release, adding the prefix **v** + **tag**.
    - e.g (tag: **1.0.0**)
    - e.g (release: **v1.0.0**)
