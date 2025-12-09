from unittest import TestCase
from unittest.mock import call

from test.mocks.RepositoryMock import RepositoryMock

from src.application.commands.AssignPullRequestIssue import AssignPullRequestIssue
from src.application.handlers.AssignIssueHandler import AssignIssueHandler
from src.application.handlers.AssignPullRequestHandler import AssignPullRequestHandler
from src.application.handlers.AssignPullRequestIssueHandler import AssignPullRequestIssueHandler
from src.driven.assignees.Adapter import Adapter as AssigneesAdapter
from src.driven.issues.Adapter import Adapter as IssuesAdapter
from src.driven.pull_requests.Adapter import Adapter as PullRequestAdapter


class AssignPullRequestIssueHandlerTest(TestCase):

    def setUp(self) -> None:
        self.repository = RepositoryMock()
        pulls = PullRequestAdapter(repository=self.repository)
        issues = IssuesAdapter(repository=self.repository)
        assignees = AssigneesAdapter(repository=self.repository)
        pull_handler = AssignPullRequestHandler(pulls=pulls, assignees=assignees)
        issue_handler = AssignIssueHandler(issues=issues, assignees=assignees)

        self.handler = AssignPullRequestIssueHandler(pulls=pull_handler, issues=issue_handler)

    def tearDown(self) -> None:
        self.repository.reset_mock()

    def test_assign_pull_requests_and_issues(self):
        """Given that I have pull requests and issues that are unassigned"""
        pulls = [{'number': 1, 'assignees': []}]
        issues = [{'number': 2, 'assignees': []}]
        self.repository.add_pull_requests(pulls=pulls)
        self.repository.add_issues(issues=issues)

        """And that the assignees are repository assignees"""
        assignees = ['user1', 'user2']
        self.repository.add_assignees(assignees=assignees)

        """And that a request for assignment of these pull requests and issues occurs"""
        command = AssignPullRequestIssue(
            actor='',
            assignees=assignees,
            allow_self_assign=True,
            allow_no_assignees=False
        )

        """When this request is executed"""
        self.handler.handle(command=command)

        """Then the pull requests should be assigned"""
        self.repository.get_pulls.assert_called_once_with()
        self.repository.get_pull.assert_has_calls([call(number=pull.get('number')) for pull in pulls])
        self.repository.get_pull.return_value.add_to_assignees.assert_called_once_with(*assignees)

        """And the issues should also be assigned"""
        self.repository.get_issues.assert_called_once_with()
        self.repository.get_issue.assert_has_calls([call(number=issue.get('number')) for issue in issues])
        self.repository.get_issue.return_value.add_to_assignees.assert_called_once_with(*assignees)
