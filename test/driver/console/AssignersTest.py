from unittest import TestCase
from unittest.mock import MagicMock

from test.mocks.handlers.AssignIssueHandlerMock import AssignIssueHandlerMock
from test.mocks.handlers.AssignPullRequestHandlerMock import AssignPullRequestHandlerMock
from test.mocks.handlers.AssignPullRequestIssueHandlerMock import AssignPullRequestIssueHandlerMock

from src.application.domain.exceptions.IssueNotAssigned import IssueNotAssigned
from src.application.domain.exceptions.PullRequestNotAssigned import PullRequestNotAssigned
from src.driver.console.Assigners import Assigners
from src.driver.console.ExitCode import ExitCode
from src.driver.console.Request import Request

class AssignersTest(TestCase):

    def setUp(self) -> None:
        self.logger = MagicMock()
        self.pull_handler = AssignPullRequestHandlerMock()
        self.issue_handler = AssignIssueHandlerMock()
        self.pull_issue_handler = AssignPullRequestIssueHandlerMock()

        self.assigners = Assigners(
            logger=self.logger,
            pull_handler=self.pull_handler,
            issue_handler=self.issue_handler,
            pull_issue_handler=self.pull_issue_handler
        )

    def tearDown(self) -> None:
        self.logger.reset_mock()
        self.pull_handler.reset()
        self.issue_handler.reset()
        self.pull_issue_handler.reset()

    def test_execute_succeeds_for_issue_only(self):
        """Given a request that targets only issues"""
        request = Request(
            actor="user3",
            options=['ISSUE'],
            assignees=['user3', 'user4'],
            allow_self_assign=True,
            allow_no_assignees=False
        )

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then SUCCESS should be returned"""
        self.assertEqual(actual.value, ExitCode.SUCCESS)

    def test_execute_succeeds_for_pull_request_only(self):
        """Given a request that targets only pull requests"""
        request = Request(
            actor="user2",
            options=['PULL_REQUEST'],
            assignees=['user2'],
            allow_self_assign=False,
            allow_no_assignees=True
        )

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then SUCCESS should be returned"""
        self.assertEqual(actual.value, ExitCode.SUCCESS)

    def test_execute_succeeds_for_pull_request_and_issue(self):
        """Given a request that targets both pull request and issue"""
        request = Request(
            actor="user1",
            options=['PULL_REQUEST', 'ISSUE'],
            assignees=['user1', 'user2'],
            allow_self_assign=True,
            allow_no_assignees=False
        )

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then SUCCESS should be returned"""
        self.assertEqual(actual.value, ExitCode.SUCCESS)

    def test_execute_when_issue_not_assigned(self):
        """Given a request that targets only issues"""
        request = Request(
            actor="user4",
            options=['ISSUE'],
            assignees=['user4', 'user5'],
            allow_self_assign=False,
            allow_no_assignees=False
        )

        """And a handler raises a issue not assigned"""
        self.issue_handler.with_exception(exception=IssueNotAssigned(assignee=request.actor))

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then ASSIGNMENT_FAILURE should be returned"""
        self.assertEqual(actual.value, ExitCode.ASSIGNMENT_FAILURE)

    def test_execute_when_pull_request_not_assigned(self):
        """Given a request that targets only pull requests"""
        request = Request(
            actor="user3",
            options=['PULL_REQUEST'],
            assignees=['user3', 'user4'],
            allow_self_assign=True,
            allow_no_assignees=False
        )

        """And a handler raises a pull request not assigned"""
        self.pull_handler.with_exception(exception=PullRequestNotAssigned(assignee=request.actor))

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then ASSIGNMENT_FAILURE should be returned"""
        self.assertEqual(actual.value, ExitCode.ASSIGNMENT_FAILURE)

    def test_execute_when_pull_request_and_issue_not_assigned(self):
        """Given a request that targets both pull requests and issues"""
        request = Request(
            actor="user5",
            options=['PULL_REQUEST', 'ISSUE'],
            assignees=['user5'],
            allow_self_assign=False,
            allow_no_assignees=True
        )

        """And a handler raises a pull request not assigned"""
        self.pull_issue_handler.with_exception(exception=PullRequestNotAssigned(assignee=request.actor))

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then ASSIGNMENT_FAILURE should be returned"""
        self.assertEqual(actual.value, ExitCode.ASSIGNMENT_FAILURE)

    def test_execute_when_invalid_assignee_options(self):
        """Given a request with invalid assignee options"""
        request = Request(
            actor="user1",
            options=[],
            assignees=['user1'],
            allow_self_assign=True,
            allow_no_assignees=False
        )

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then CONFIGURATION_MISSING should be returned"""
        self.assertEqual(actual.value, ExitCode.CONFIGURATION_MISSING)

    def test_execute_when_unexpected_failure(self):
        """Given a request that targets only issues"""
        request = Request(
            actor="user2",
            options=['ISSUE'],
            assignees=['user2', 'user3'],
            allow_self_assign=False,
            allow_no_assignees=True
        )

        """And a handler raises an unexpected exception"""
        self.issue_handler.with_exception(exception=Exception("Unexpected error"))

        """When execute is called"""
        actual = self.assigners.execute(request=request)

        """Then GENERAL_ERROR should be returned"""
        self.assertEqual(actual.value, ExitCode.UNEXPECTED_FAILURE)
