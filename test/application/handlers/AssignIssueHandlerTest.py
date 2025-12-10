from typing import List
from unittest import TestCase
from unittest.mock import call

from test.application.factories.command import assign_issues
from test.mocks.RepositoryMock import RepositoryMock

from parameterized import parameterized

from src.application.domain.exceptions.IssueNotAssigned import IssueNotAssigned
from src.application.domain.exceptions.MissingAssignees import MissingAssignees
from src.application.handlers.AssignIssueHandler import AssignIssueHandler
from src.driven.assignees.Adapter import Adapter as AssigneesAdapter
from src.driven.issues.Adapter import Adapter as IssuesAdapter


class AssignIssueHandlerTest(TestCase):

    def setUp(self) -> None:
        self.repository = RepositoryMock()
        issues = IssuesAdapter(repository=self.repository)
        assignees = AssigneesAdapter(repository=self.repository)
        self.handler = AssignIssueHandler(issues=issues, assignees=assignees)

    def tearDown(self) -> None:
        self.repository.reset_mock()

    @parameterized.expand([
        (['user1'], [{'number': 1, 'assignees': []}],),
        (['user1', 'user2'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],),
        (['user1', 'user2', 'user3'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],)])
    def test_assign_with_unassigned_issues(self, assignees: List[str], issues: List[dict]):
        """Given that I have issues that have not been assigned to any user"""
        self.repository.add_issues(issues=issues)

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        """And that a request for assignment of these issues occurs"""
        command = assign_issues(assignees=assignees)

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the issues should be assigned"""
        self.repository.get_issues.assert_called_once()
        self.repository.get_issues.assert_called_with()
        self.repository.get_issue.assert_has_calls([call(number=issue.get('number')) for issue in issues])

    @parameterized.expand([
        (['user1'], [{'number': 1, 'assignees': ['user10']}],),
        (['user1', 'user2'], [{'number': 1, 'assignees': ['user10']}, {'number': 2, 'assignees': ['user10']}],),
        (['user1', 'user2', 'user3'], [{'number': 1, 'assignees': ['user10']}, {'number': 2, 'assignees': ['user10']}],)
    ])
    def test_assign_when_already_assigned_issues(self, assignees: List[str], issues: List[dict]):
        """Given that I have issues that have already been assigned to a user"""
        self.repository.add_issues(issues=issues)

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        """And that a request for assignment of these issues occurs"""
        command = assign_issues(assignees=assignees)

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the issues should not be assigned again"""
        self.repository.get_issues.assert_called_once()
        self.repository.get_issues.assert_called_with()
        self.repository.get_issue.assert_not_called()

    @parameterized.expand([(['user1'],), (['user1', 'user2'],), (['user1', 'user2', 'user3'],)])
    def test_assign_with_no_issues(self, assignees: List[str]):
        """Given that there are no issues in the repository"""
        self.repository.remove_issues()

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        """And that a request for assignment of these issues occurs"""
        command = assign_issues(assignees=assignees)

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then no issues should be assigned"""
        self.repository.get_issues.assert_called_once()
        self.repository.get_issues.assert_called_with()
        self.repository.get_issue.assert_not_called()

    @parameterized.expand([
        (['user1'], [{'number': 1, 'assignees': []}],),
        (['user1', 'user2'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],),
        (['user1', 'user2', 'user3'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],)])
    def test_exception_when_missing_assignees(self, assignees: List[str], issues: List[dict]):
        """Given that I have issues that have not been assigned to any user"""
        self.repository.add_issues(issues=issues)

        """And there is a request for the assignment of these issues"""
        command = assign_issues(assignees=assignees, allow_no_assignees=False)

        """And that the assignee of the request is not an available assignee"""
        self.repository.remove_assignees(assignees=command.assignees)

        with self.assertRaises(MissingAssignees) as context:
            """When this request is executed"""
            self.handler.handle(command=command)

        """Then an error indicating missing are assignees should occur"""
        self.assertEqual('Missing assignees.', context.exception.message)

    @parameterized.expand([
        (['user1'], [{'number': 1, 'assignees': []}],),
        (['user1', 'user2'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],),
        (['user1', 'user2', 'user3'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],)])
    def test_exception_when_issue_not_assigned(self, assignees: List[str], issues: List[dict]):
        """Given that I have issues that have not been assigned to any user"""
        self.repository.add_issues(issues=issues)

        """And there is a request for the assignment of these issues"""
        command = assign_issues(
            assignees=assignees,
            actor=assignees[0],
            allow_self_assign=False,
            allow_no_assignees=False
        )

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        with self.assertRaises(IssueNotAssigned) as context:
            """When this request is executed"""
            self.handler.handle(command=command)

        """Then an error indicating issue not assigned should occur"""
        self.assertEqual(f"Not allowed to assign issues to self <{command.actor}>.", context.exception.message)

    @parameterized.expand([(['user1'],), (['user1', 'user2'],)])
    def test_assign_when_self_assignment_allowed(self, assignees: List[str]):
        """Given that I have issues that have not been assigned to any user"""
        issues = [{'number': 1, 'assignees': []}]
        self.repository.add_issues(issues=issues)

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        """And that the actor is one of the assignees but self-assign is allowed"""
        command = assign_issues(
            assignees=assignees,
            actor=assignees[0],
            allow_self_assign=True,
            allow_no_assignees=False
        )

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the issue should be assigned even with the actor in the list"""
        self.repository.get_issues.assert_called_once()
        self.repository.get_issue.assert_called_once_with(number=issues[0].get('number'))

    def test_assign_when_allowing_no_assignees(self):
        """Given that I have issues but allow no assignees"""
        issues = [{'number': 1, 'assignees': []}]
        self.repository.add_issues(issues=issues)

        """And the repository has no assignees configured"""
        self.repository.add_assignees(assignees=[])

        """And there is a request without providing assignees but allowing the condition"""
        command = assign_issues(assignees=[], allow_no_assignees=True)

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the handler should skip assigning since there are no assignees"""
        self.repository.get_issues.assert_called_once()
        self.repository.get_issue.assert_not_called()
