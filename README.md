# Auto assign

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

* [Overview](#overview)
* [How to use](#how-to-use)
* [License](#license)
* [Contributing](#contributing)

<div id='overview'></div> 

## Overview

GitHub action that automatically assigns issues and pull requests to specified assignees.

<div id='how-to-use'></div>

## How to use

Before configuring your `.yml` file, let's understand the configuration parameters.

| Parameter            |  Type   | Required | Default | Description                                                                                                                | 
|:---------------------|:-------:|:--------:|:-------:|----------------------------------------------------------------------------------------------------------------------------|
| `assignees`          | string  |   Yes    |   N/A   | Comma-separated list of usernames. Assignments will be made to them.                                                       |
| `github_token`       | string  |   Yes    |   N/A   | GitHub app installation [access token](https://docs.github.com/en/actions/security-guides/automatic-token-authentication). |
| `allow_self_assign`  | boolean |    No    |  True   | Flag that allows self-assignment to an issue or pull request.                                                              |
| `allow_no_assignees` | boolean |    No    |  False  | Flag that prevents the action from failing when there are no assignees.                                                    |
| `assignment_options` | string  |    No    |  ISSUE  | Assignment options in a GitHub action related to automatically assigning issues and pull requests.                         |

By default, write permission allows the GitHub action only to create and edit issues in **public repositories**.
You must use admin permission or a more restricted setting for **private repositories**.
You can generate a personal access token with the required scopes.

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
        uses: gustavofreze/auto-assign@1.0.0
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
        uses: gustavofreze/auto-assign@1.0.0
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
        uses: gustavofreze/auto-assign@1.0.0
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
        uses: gustavofreze/auto-assign@1.0.0
        with:
          assignees: 'user1,user2'
          github_token: '${{ secrets.GITHUB_TOKEN }}'
          allow_self_assign: 'true'
          allow_no_assignees: 'true'
          assignment_options: 'ISSUE,PULL_REQUEST'
```

<div id='license'></div>

## License

Auto-assign is licensed under [MIT](LICENSE).

<div id='contributing'></div>

## Contributing

Please follow the [contributing guidelines](CONTRIBUTING.md) to contribute to the project.
