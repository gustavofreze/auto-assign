# Auto assign

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

* [Overview](#overview)
* [How to use](#how-to-use)
* [License](#license)
* [Contributing](#contributing)

<div id='overview'></div> 

## Overview

GitHub Action that automatically assigns issues and pull requests to specified assignees.

<div id='how-to-use'></div>

## How to use

### Quick start

The smallest setup assigns every new issue and pull request to one login, with the default workflow token:

```yml
name: Auto assign

on:
  issues:
    types:
      - opened
  pull_request:
    types:
      - opened

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
      - name: Assign issues and pull requests
        uses: gustavofreze/auto-assign@x.y.z
        with:
          assignees: 'user1'
          assignment_options: 'ISSUE,PULL_REQUEST'
```

### Parameters

| Parameter            |  Type   | Required |    Default     | Description                                                                                                                                                   |
|:---------------------|:-------:|:--------:|:--------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `assignees`          | string  |   Yes    |      N/A       | Comma-separated list of logins to assign.                                                                                                                     |
| `github_token`       | string  |    No    | `github.token` | Token used to call the GitHub API. The default [workflow token](https://docs.github.com/en/actions/security-guides/automatic-token-authentication) is enough. |
| `assignment_options` | string  |    No    |    `ISSUE`     | What to assign: `ISSUE`, `PULL_REQUEST`, or `ISSUE,PULL_REQUEST`.                                                                                             |
| `allow_self_assign`  | boolean |    No    |     `true`     | Allows the user who started the workflow to be assigned.                                                                                                      |
| `allow_no_assignees` | boolean |    No    |    `false`     | Lets the run succeed when no assignee remains, instead of reporting code `2`.                                                                                 |
| `assign_author`      | boolean |    No    |    `false`     | Also assigns the author of each issue or pull request.                                                                                                        |
| `skip_bots`          | boolean |    No    |    `false`     | Skips issues and pull requests opened by bots, such as `dependabot[bot]`.                                                                                     |
| `skip_drafts`        | boolean |    No    |    `false`     | Skips draft pull requests.                                                                                                                                    |

### Permissions

The job needs `issues: write` to assign issues and `pull-requests: write` to assign pull requests, in public and
private repositories alike. The default workflow token is enough. A personal access token is only needed to act
across repositories, and then it needs write access to the issues and pull requests of the target repository.

Logins that cannot be assigned in the repository are left out. When none of `assignees` can be assigned and
`allow_no_assignees` is `false`, the run reports code `2`.

### Which items are assigned

- When an `issues`, `pull_request`, `pull_request_target`, or `issue_comment` event triggers the workflow, only the
  issue or pull request from that event is assigned, if it has no assignee yet. A pull request event never assigns
  issues, and an issue event never assigns pull requests.
- When any other event triggers the workflow (`workflow_dispatch`, `schedule`), every open issue and pull request
  without an assignee is assigned, according to `assignment_options`.

### Self-assignment

When `allow_self_assign` is `false`, the user who started the workflow is never assigned:

- With `allow_no_assignees` set to `false`, the run reports code `2` if that user is among the assignees.
- With `allow_no_assignees` set to `true`, that user is left out and the other assignees are assigned. When no other
  assignee remains, nothing is assigned and no error occurs.

### Author, bots, and drafts

- With `assign_author` set to `true`, the author of each issue or pull request is assigned too, on top of
  `assignees`. The author is assigned even when `allow_self_assign` is `false`, because the flag asks for it
  explicitly. GitHub ignores an author who cannot be assigned in the repository.
- With `skip_bots` set to `true`, issues and pull requests opened by a bot (a login ending in `[bot]`, such as
  `dependabot[bot]`) are left untouched.
- With `skip_drafts` set to `true`, draft pull requests are left untouched.

### Working only with issues

Example of how to configure your `.yml` file to auto-assign users only for **issues**.

```yml
name: Auto assign issues

on:
  issues:
    types:
      - opened

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Assign issues
        uses: gustavofreze/auto-assign@x.y.z
        with:
          assignees: 'user1,user2'
          github_token: '${{ secrets.GITHUB_TOKEN }}'
          assignment_options: 'ISSUE'
```

### Working only with pull request

Example of how to configure your `.yml` file to auto-assign users only for **pull requests**.

```yml
name: Auto assign pull requests

on:
  pull_request:
    types:
      - opened

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - name: Assign pull requests
        uses: gustavofreze/auto-assign@x.y.z
        with:
          assignees: 'user1,user2'
          github_token: '${{ secrets.GITHUB_TOKEN }}'
          assignment_options: 'PULL_REQUEST'
```

### Working with issues and pull requests

Example of how to configure your `.yml` file to auto-assign users for **issues** and **pull requests**.

```yml
name: Auto assign issues and pull requests

on:
  issues:
    types:
      - opened
  pull_request:
    types:
      - opened

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
      - name: Assign issues and pull requests
        uses: gustavofreze/auto-assign@x.y.z
        with:
          assignees: 'user1,user2'
          github_token: '${{ secrets.GITHUB_TOKEN }}'
          assignment_options: 'ISSUE,PULL_REQUEST'
```

### Working with issues and pull requests in a non-restrictive way

Example of configuring your `.yml` file to automatically assign users for **issues** and **pull requests**.

The difference in approach consists of the following:

- If the only assignable user were the one who started the workflow, it would be assigned.
- No items will be assigned if users are not assignable, including those who started the workflow.
  However, no error will occur.

```yml
name: Auto assign issues and pull requests

on:
  issues:
    types:
      - opened
  pull_request:
    types:
      - opened

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
      - name: Assign issues and pull requests
        uses: gustavofreze/auto-assign@x.y.z
        with:
          assignees: 'user1,user2'
          github_token: '${{ secrets.GITHUB_TOKEN }}'
          allow_self_assign: 'true'
          allow_no_assignees: 'true'
          assignment_options: 'ISSUE,PULL_REQUEST'
```

### Assigning the author and skipping bots and drafts

Example of assigning each pull request to its author and a reviewer, while leaving drafts and bot pull requests alone.

```yml
name: Auto assign pull requests

on:
  pull_request:
    types:
      - opened
      - ready_for_review

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - name: Assign pull requests
        uses: gustavofreze/auto-assign@x.y.z
        with:
          assignees: 'reviewer1'
          skip_bots: 'true'
          skip_drafts: 'true'
          assign_author: 'true'
          assignment_options: 'PULL_REQUEST'
```

<div id='output'></div>

### Output

The action writes a single output, `result`, a JSON object that describes the run. Read it with `fromJSON`, for
example `fromJSON(steps.autoassign.outputs.result).status`.

| Field                  | Type    | Description                                                                                                  |
|:-----------------------|:--------|:-------------------------------------------------------------------------------------------------------------|
| `result.code`          | Integer | Outcome of the run: `0` success, `1` unexpected error, `2` assignment refused, `3` missing or invalid input. |
| `result.status`        | String  | Name of the code: `SUCCESS`, `UNEXPECTED_FAILURE`, `ASSIGNMENT_FAILURE`, or `CONFIGURATION_MISSING`.         |
| `result.message`       | String  | What happened, in one sentence: the counts on success, the reason on failure.                                |
| `result.issues`        | Array   | Issues assigned in this run, each as `{"number": 1, "assignees": ["alice"]}`.                                |
| `result.pull_requests` | Array   | Pull requests assigned in this run, in the same shape as `issues`.                                           |

The step itself never fails: every outcome, including a failure, is reported through `result`, so the workflow
decides how to react. Each run also writes a step summary listing every assigned issue and pull request with its
assignees, and an expected failure is shown as an error annotation on the workflow run with the same text as
`result.message`.

#### Example output

A successful run triggered by an opened issue (the output is written on one line, shown formatted here):

```json
{
    "code": 0,
    "status": "SUCCESS",
    "message": "Assigned 1 issue and 0 pull requests.",
    "issues": [
        {
            "number": 1,
            "assignees": [
                "gustavofreze"
            ]
        }
    ],
    "pull_requests": []
}
```

Its step summary:

> ### Auto assign
>
> | Item     | Assignees    |
> |:---------|:-------------|
> | Issue #1 | gustavofreze |

A run that refuses a self-assignment, with `allow_self_assign` and `allow_no_assignees` set to `false`, shows the
annotation `Not allowed to self-assign <gustavofreze>.` on the workflow run, and the summary says
`Nothing was assigned.`:

```json
{
    "code": 2,
    "status": "ASSIGNMENT_FAILURE",
    "message": "Not allowed to self-assign <gustavofreze>.",
    "issues": [],
    "pull_requests": []
}
```

A run with required inputs missing names all of them at once:

```json
{
    "code": 3,
    "status": "CONFIGURATION_MISSING",
    "message": "Required environment variables are missing <INPUT_ASSIGNEES, INPUT_GITHUB_TOKEN>.",
    "issues": [],
    "pull_requests": []
}
```

The assigned items can feed later steps, for example to comment on each assigned pull request:

```yml
      - name: Comment on assigned pull requests
        if: ${{ fromJSON(steps.autoassign.outputs.result).pull_requests[0] != null }}
        env:
          GH_TOKEN: '${{ github.token }}'
          RESULT: '${{ steps.autoassign.outputs.result }}'
        run: |
          for number in $(echo "${RESULT}" | jq '.pull_requests[].number'); do
            gh pr comment "${number}" --repo "${GITHUB_REPOSITORY}" --body "Assigned automatically."
          done
```

The example below reacts to each outcome through `result.status`:

```yml
name: Auto assign issues and pull requests

on:
  issues:
    types:
      - opened
  pull_request:
    types:
      - opened

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
      - name: Assign issues and pull requests
        id: autoassign
        uses: gustavofreze/auto-assign@x.y.z
        with:
          assignees: 'user1,user2'
          github_token: '${{ secrets.GITHUB_TOKEN }}'
          allow_self_assign: 'true'
          allow_no_assignees: 'true'
          assignment_options: 'ISSUE,PULL_REQUEST'

      - name: Success logic
        if: ${{ fromJSON(steps.autoassign.outputs.result).status == 'SUCCESS' }}
        run: |
          echo "Assignment completed successfully."

      - name: Unexpected error handling
        if: ${{ fromJSON(steps.autoassign.outputs.result).status == 'UNEXPECTED_FAILURE' }}
        run: |
          echo "An unexpected error occurred during execution."

      - name: Assignment failure handling
        if: ${{ fromJSON(steps.autoassign.outputs.result).status == 'ASSIGNMENT_FAILURE' }}
        run: |
          echo "The action failed to assign issues or pull requests."

      - name: Configuration failure handling
        if: ${{ fromJSON(steps.autoassign.outputs.result).status == 'CONFIGURATION_MISSING' }}
        run: |
          echo "A required configuration value is missing or invalid."
```

<div id='license'></div>

## License

Auto-assign is licensed under [MIT](LICENSE).

<div id='contributing'></div>

## Contributing

Please follow the [contributing guidelines](CONTRIBUTING.md) to contribute to the project.
