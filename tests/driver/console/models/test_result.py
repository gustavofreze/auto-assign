import json

import pytest

from src.driver.console.models.result import Result


@pytest.mark.parametrize(
    ids=['one of each', 'none assigned', 'several of each'],
    argnames=['issues', 'pull_requests', 'message'],
    argvalues=[
        ([{'number': 1, 'assignees': ['alice']}], [{'number': 7, 'assignees': ['bob']}],
         'Assigned 1 issue and 1 pull request.'),
        ([], [], 'Assigned 0 issues and 0 pull requests.'),
        (
            [{'number': 1, 'assignees': ['alice']}, {'number': 3, 'assignees': ['alice']}],
            [{'number': 7, 'assignees': ['bob']}, {'number': 8, 'assignees': ['bob']}],
            'Assigned 2 issues and 2 pull requests.'
        )
    ]
)
def test_to_json_when_the_run_succeeds_then_the_message_counts_the_assigned_items(
        issues: list[dict[str, object]],
        message: str,
        pull_requests: list[dict[str, object]]
) -> None:
    # When a successful result is written with the assigned items
    document = Result.success().to_json(issues=issues, pull_requests=pull_requests)

    # Then the document carries the success status, a counting message, and the items
    assert json.loads(document) == {
        'code': 0,
        'status': 'SUCCESS',
        'message': message,
        'issues': issues,
        'pull_requests': pull_requests
    }


@pytest.mark.parametrize(
    ids=['unexpected failure', 'assignment failure', 'configuration missing'],
    argnames=['result', 'code', 'status'],
    argvalues=[
        (Result.unexpected_failure(message='boom'), 1, 'UNEXPECTED_FAILURE'),
        (Result.assignment_failure(message='boom'), 2, 'ASSIGNMENT_FAILURE'),
        (Result.configuration_missing(message='boom'), 3, 'CONFIGURATION_MISSING')
    ]
)
def test_to_json_when_the_run_fails_then_the_document_carries_the_failure_status_and_message(
        code: int,
        result: Result,
        status: str
) -> None:
    # When a failed result is written
    document = result.to_json(issues=[], pull_requests=[])

    # Then the document carries the code, the status, the failure message, and no item
    assert json.loads(document) == {
        'code': code,
        'status': status,
        'message': 'boom',
        'issues': [],
        'pull_requests': []
    }
