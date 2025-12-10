from unittest import TestCase

from test.mocks.RepositoryMock import RepositoryMock
from github.GithubException import GithubException

from src.driven.assignees.Adapter import Adapter


class AdapterTest(TestCase):

    def setUp(self) -> None:
        self.repository = RepositoryMock()
        self.adapter = Adapter(repository=self.repository)

    def tearDown(self) -> None:
        self.repository.reset_mock()

    def test_exception_handling(self):
        """Given that an exception is raised when retrieving assignees"""
        self.repository.with_assignees_exception(
            exception=GithubException(
                status=500,
                data='Internal Server Error',
                headers={}
            )
        )

        """When exists is called"""
        assignees = self.adapter.exists(assignees=['user1', 'user2', 'user3'])

        """Then an empty list should be returned"""
        self.assertEqual([], assignees)

    def test_returns_valid_assignees_only(self):
        """Given that repository assignees are configured"""
        self.repository.add_assignees(assignees=['user1', 'user2'])

        """When exists is called with a mix of valid and invalid values"""
        assignees = self.adapter.exists(assignees=['user1', 'user3'])

        """Then only valid assignees should be returned"""
        self.assertEqual(['user1'], assignees)
        self.repository.get_assignees.assert_called_once_with()
