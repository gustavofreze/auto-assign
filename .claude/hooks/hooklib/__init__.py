"""Shared internal library for the Claude Code hooks in this folder.

Self-contained: Python stdlib only, resolved from this directory because every entry
point lives beside it. `core` holds the language-agnostic scaffolding (payload parsing,
violations, reporting). `python` is the Python language module behind the language seam,
a later language module can sit beside it without touching `core`.
"""
