---
description: Consumption rules for the container image this action builds, base image pinning, build context, lean layers, and secrets.
paths:
  - "Dockerfile*"
  - ".dockerignore"
  - "*.dockerignore"
---

# Container image

The action runs as a Docker container action (`runs.using: docker` in `action.yml`), so `Dockerfile` is shipped code.
It consumes a shared Python base image and adds only this action's dependencies and source.

## Pre-output checklist

Verify every item before producing a Dockerfile or dockerignore.

1. The first line is `# syntax=docker/dockerfile:1`, which pins the stable BuildKit frontend.
2. `FROM` names the base image by its Python-minor alias (`3.14-builder`, `3.14-runtime`), never `latest` and never a
   versioned tag such as `3.14-runtime-1.0.9`. The runner builds the action image on every run, so the alias hands
   every run the base family's latest security rebuild. The Python minor in the tag matches the floor in
   `pyproject.toml`.
3. The app never re-declares what its base already provides (the interpreter, Poetry, the non-root user). Where the
   base does not provide something the action needs, the app declares it.
4. A `.dockerignore` sits next to the `Dockerfile` and excludes `.git`, `.venv`, `.claude`, `tests`, `htmlcov`,
   `.coverage`, and every `.env*` file. Secrets never enter the build context.
5. Dependency layers come before code layers: copy `pyproject.toml` (and the lock file when one is tracked), install,
   then copy `src`. Development dependencies are not installed in the shipped image (`poetry install --only main`).
6. One `RUN` per concern, with its cache cleaned in the same layer. `COPY`, never `ADD`.
7. No build argument or `ENV` carries a credential. The GitHub token reaches the container at run time through the
   action inputs, never at build time.
8. The image carries no comment other than the syntax directive. Labels (`org.opencontainers.image.*`) carry the
   metadata.
9. The build is multi-stage: the `builder` target installs the virtual environment, the `runtime` target receives
   `/app` from it with `COPY --from=builder --chown=app:app`. Nothing from the builder toolchain ships.
10. The final stage ends with `USER 0`. This is the one sanctioned override of the non-root base: a Docker container
    action must run as root, because the runner mounts `GITHUB_WORKSPACE` and the `GITHUB_OUTPUT` file with the
    runner's own ownership, and the base user cannot write them.
11. The entrypoint starts the interpreter with `-P` (`CMD ["python3", "-P", "-m", "src.main"]`). The runner sets the
    working directory to `/github/workspace`, the caller's checkout, and without `-P` that directory leads
    `sys.path`, so a caller's own `src/main.py` would run in place of the action.
12. hadolint passes as part of `make review`. `COPY` destinations are absolute (`/app/...`), because the base sets the
    working directory and hadolint cannot see it. Every hadolint exception lives in `.hadolint.yaml` with its reason,
    never inline in the `Dockerfile`.

## Tooling image

The `Makefile` runs every Python command in the base family's `cli` target through the same kind of alias
(`3.14-cli`), so tooling and the shipped image take the same security rebuilds.
