#!/usr/bin/env python3
"""Guard keeping `.env` files out of Write and Bash (PreToolUse).

`<root>/.env.local` is the one env file local development owns, so reading,
writing, and rewriting it are allowed. Every other `.env` Write or read is
blocked, along with the `git ls-files` inspection carve-out `skeleton-layout`
needs. A speed bump, not a sandbox: Bash is unbounded and the verb list is
evadable. The strong guarantee stays with the enumerated `.env` deny in
`settings.json`, which leaves `./.env.local` out and denies the rest.
"""

import json
import re
import sys
from pathlib import Path
from typing import Final

from hooklib.core import project_root

# A `.env` token: the literal `.env`, not a longer word such as `.environment`.
ENV_TOKEN: Final = re.compile(r"\.env\b")

# Reading, copying, or moving verbs, and the `.` (source) builtin in command position.
BLOCKED_VERBS: Final = re.compile(
    r"\b(cat|head|tail|less|more|tee|cp|mv|sed|awk|base64|xxd|strings|source|curl|wget)\b"
)
SOURCE_BUILTIN: Final = re.compile(r"(?:^|[\s;&|(])\.(?=\s)")

# Every `.env` name a command cites, so a command touching only `.env.local` passes.
# `.env.local.bak` reads as its own name and stays blocked.
ENV_NAME: Final = re.compile(r"\.env(?:\.[A-Za-z0-9_-]+)*")


def block(message: str) -> int:
    """Print the reason to stderr and return the blocking exit code."""
    print(message, file=sys.stderr)
    return 2


def is_env_name(name: str) -> bool:
    """Whether a basename is a `.env` or `.env.*` file."""
    return name == ".env" or name.startswith(".env.")


def check_write(tool_input: dict) -> int:
    """Allow a Write only when it targets `<root>/.env.local`, new or existing."""
    file_path = tool_input.get("file_path")

    if not isinstance(file_path, str) or not is_env_name(Path(file_path).name):
        return 0

    resolved = Path(file_path).resolve()
    target = (project_root() / ".env.local").resolve()

    if resolved != target:
        return block(f"Refusing to Write {file_path}: the only writable env file is {target}.")
    return 0


def check_bash(tool_input: dict) -> int:
    """Block a Bash command that pairs a `.env` token with a reading verb."""
    command = tool_input.get("command")

    if not isinstance(command, str) or not ENV_TOKEN.search(command):
        return 0

    if command.strip().startswith("git ls-files"):
        return 0

    if all(name == ".env.local" for name in ENV_NAME.findall(command)):
        return 0

    if BLOCKED_VERBS.search(command) or SOURCE_BUILTIN.search(command) or ">" in command:
        return block(f"Refusing to run a .env-touching command: {command}.")
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}

    if tool_name == "Write":
        return check_write(tool_input)
    if tool_name == "Bash":
        return check_bash(tool_input)
    return 0


if __name__ == "__main__":
    sys.exit(main())
