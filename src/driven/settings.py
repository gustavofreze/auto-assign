from typing import List

from src.driven.Environment import Environment

ASSIGNEES: List[str] = Environment.get(variable='INPUT_ASSIGNEES').to_list()
GITHUB_ACTOR: str = Environment.get(variable='GITHUB_ACTOR').to_str()
GITHUB_TOKEN: str = Environment.get(variable='INPUT_GITHUB_TOKEN').to_str()
GITHUB_REPOSITORY: str = Environment.get(variable='GITHUB_REPOSITORY').to_str()
ALLOW_SELF_ASSIGN: bool = Environment.get(variable='INPUT_ALLOW_SELF_ASSIGN').to_bool()
ASSIGNMENT_OPTIONS: List[str] = Environment.get(variable='INPUT_ASSIGNMENT_OPTIONS').to_list()
ALLOW_NO_ASSIGNEES: bool = Environment.get(variable='INPUT_ALLOW_NO_ASSIGNEES').to_bool()
