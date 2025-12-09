from typing import List
from unittest import TestCase
from unittest.mock import call

from test.application.factories.command import assign_pull_requests
from test.mocks.RepositoryMock import RepositoryMock

from parameterized import parameterized

from src.application.domain.exceptions.MissingAssignees import MissingAssignees
from src.application.domain.exceptions.PullRequestNotAssigned import PullRequestNotAssigned
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler
from src.driven.assignees.Adapter import Adapter as AssigneesAdapter
from src.driven.pull_requests.Adapter import Adapter as PullRequestAdapter


class AssignPullRequestHandlerTest(TestCase):

    def setUp(self) -> None:
        self.repository = RepositoryMock()
        pulls = PullRequestAdapter(repository=self.repository)
        assignees = AssigneesAdapter(repository=self.repository)
        self.handler = AssignPullRequestHandler(pulls=pulls, assignees=assignees)

    def tearDown(self) -> None:
        self.repository.reset_mock()

    @parameterized.expand([
        (['user1'], [{'number': 1, 'assignees': []}],),
        (['user1', 'user2'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],),
        (['user1', 'user2', 'user3'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],)])
    def test_assign_with_unassigned_pull_requests(self, assignees: List[str], pulls: List[dict]):
        """Given that I have pull requests that have not been assigned to any user"""
        self.repository.add_pull_requests(pulls=pulls)

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        """And that a request for assignment of these pull request occurs"""
        command = assign_pull_requests(assignees=assignees)

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the pull request should be assigned"""
        self.repository.get_pulls.assert_called_once()
        self.repository.get_pulls.assert_called_with()
        self.repository.get_pull.assert_has_calls([call(number=pull.get('number')) for pull in pulls])

    @parameterized.expand([
        (['user1'], [{'number': 1, 'assignees': ['user10']}],),
        (['user1', 'user2'], [{'number': 1, 'assignees': ['user10']}, {'number': 2, 'assignees': ['user10']}],),
        (['user1', 'user2', 'user3'], [{'number': 1, 'assignees': ['user10']}, {'number': 2, 'assignees': ['user10']}],)
    ])
    def test_assign_when_already_assigned_pull_requests(self, assignees: List[str], pulls: List[dict]):
        """Given that I have pull requests that have already been assigned to a user"""
        self.repository.add_pull_requests(pulls=pulls)

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        """And that a request for assignment of these pull request occurs"""
        command = assign_pull_requests(assignees=assignees)

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the pull request should be assigned"""
        self.repository.get_pulls.assert_called_once()
        self.repository.get_pulls.assert_called_with()
        self.repository.get_pull.assert_not_called()

    @parameterized.expand([(['user1'],), (['user1', 'user2'],), (['user1', 'user2', 'user3'],)])
    def test_assign_with_no_pull_requests(self, assignees: List[str]):
        """Given that there are no pull requests in the repository"""
        self.repository.remove_pull_requests()

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        """And that a request for assignment of these pull request occurs"""
        command = assign_pull_requests(assignees=assignees)

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the pull request should be assigned"""
        self.repository.get_pulls.assert_called_once()
        self.repository.get_pulls.assert_called_with()
        self.repository.get_pull.assert_not_called()

    @parameterized.expand([
        (['user1'], [{'number': 1, 'assignees': []}],),
        (['user1', 'user2'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],),
        (['user1', 'user2', 'user3'], [{'number': 1, 'assignees': []}, {'number': 2, 'assignees': []}],)])
    def test_exception_when_missing_assignees(self, assignees: List[str], pulls: List[dict]):
        """Given that I have pull requests that have not been assigned to any user"""
        self.repository.add_pull_requests(pulls=pulls)

        """And there is a request for the assignment of these pull requests"""
        command = assign_pull_requests(assignees=assignees, allow_no_assignees=False)

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
    def test_exception_when_pull_request_not_assigned(self, assignees: List[str], pulls: List[dict]):
        """Given that I have pull requests that have not been assigned to any user"""
        self.repository.add_pull_requests(pulls=pulls)

        """And there is a request for the assignment of these pull requests"""
        command = assign_pull_requests(
            assignees=assignees,
            actor=assignees[0],
            allow_self_assign=False,
            allow_no_assignees=False
        )

        """And that the assignees are repository assignees"""
        self.repository.add_assignees(assignees=assignees)

        with self.assertRaises(PullRequestNotAssigned) as context:
            """When this request is executed"""
            self.handler.handle(command=command)

        """Then an error indicating pull request not assigned should occur"""
        self.assertEqual(f"Not allowed to assign pull requests to self <{command.actor}>.", context.exception.message)
