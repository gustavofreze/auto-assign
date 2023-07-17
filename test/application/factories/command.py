from typing import List

from src.application.commands.AssignIssues import AssignIssues
from src.application.commands.AssignPullRequests import AssignPullRequests


def assign_issues(
        assignees: List[str],
        actor: str = '',
        allow_self_assign: bool = True,
        allow_no_assignees: bool = True
) -> AssignIssues:
    return AssignIssues(
        actor=actor,
        assignees=assignees,
        allow_self_assign=allow_self_assign,
        allow_no_assignees=allow_no_assignees
    )


def assign_pull_requests(
        assignees: List[str],
        actor: str = '',
        allow_self_assign: bool = True,
        allow_no_assignees: bool = True
) -> AssignPullRequests:
    return AssignPullRequests(
        actor=actor,
        assignees=assignees,
        allow_self_assign=allow_self_assign,
        allow_no_assignees=allow_no_assignees
    )
