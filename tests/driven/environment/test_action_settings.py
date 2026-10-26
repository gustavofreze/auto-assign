import pytest

from src.driven.environment.action_settings import ActionSettings
from src.driven.environment.assignment_preferences import AssignmentPreferences
from src.driven.environment.missing_action_input import MissingActionInput
from src.driven.environment.triggering_event import TriggeringEvent

REQUIRED_INPUTS = {
    'GITHUB_ACTOR': 'octocat',
    'INPUT_ASSIGNEES': ' alice , bob,, ',
    'GITHUB_REPOSITORY': 'octocat/hello-world',
    'INPUT_GITHUB_TOKEN': 'placeholder-token'
}


def test_from_environment_when_only_required_inputs_are_present_then_optional_inputs_take_their_defaults() -> None:
    # When the settings are read from an environment holding only the required inputs
    settings = ActionSettings.from_environment(environment=REQUIRED_INPUTS)

    # Then every input is parsed, and the optional ones take the defaults declared in action.yml
    assert settings == ActionSettings(
        actor='octocat',
        event=TriggeringEvent.repository_scan(),
        assignees=('alice', 'bob'),
        repository='octocat/hello-world',
        preferences=AssignmentPreferences(
            skip_bots=False,
            skip_drafts=False,
            assign_author=False,
            allow_self_assign=True,
            allow_no_assignees=False
        ),
        github_token='placeholder-token',
        assignment_options=('ISSUE',)
    )


@pytest.mark.parametrize(
    ids=['all enabled', 'enabled with padding and capitals', 'all disabled', 'blank takes the default'],
    argnames=['optional_inputs', 'expected'],
    argvalues=[
        (
            {
                'INPUT_SKIP_BOTS': 'true',
                'INPUT_SKIP_DRAFTS': 'true',
                'INPUT_ASSIGN_AUTHOR': 'true',
                'INPUT_ALLOW_SELF_ASSIGN': 'true',
                'INPUT_ALLOW_NO_ASSIGNEES': 'true'
            },
            AssignmentPreferences(
                skip_bots=True,
                skip_drafts=True,
                assign_author=True,
                allow_self_assign=True,
                allow_no_assignees=True
            )
        ),
        (
            {'INPUT_SKIP_BOTS': ' TRUE ', 'INPUT_SKIP_DRAFTS': 'True\n', 'INPUT_ALLOW_NO_ASSIGNEES': '  true'},
            AssignmentPreferences(
                skip_bots=True,
                skip_drafts=True,
                assign_author=False,
                allow_self_assign=True,
                allow_no_assignees=True
            )
        ),
        (
            {
                'INPUT_SKIP_BOTS': 'false',
                'INPUT_SKIP_DRAFTS': 'false',
                'INPUT_ASSIGN_AUTHOR': 'no',
                'INPUT_ALLOW_SELF_ASSIGN': 'false',
                'INPUT_ALLOW_NO_ASSIGNEES': 'false'
            },
            AssignmentPreferences(
                skip_bots=False,
                skip_drafts=False,
                assign_author=False,
                allow_self_assign=False,
                allow_no_assignees=False
            )
        ),
        (
            {'INPUT_ALLOW_SELF_ASSIGN': '  '},
            AssignmentPreferences(
                skip_bots=False,
                skip_drafts=False,
                assign_author=False,
                allow_self_assign=True,
                allow_no_assignees=False
            )
        )
    ]
)
def test_from_environment_when_optional_flags_are_present_then_they_set_the_preferences(
        expected: AssignmentPreferences,
        optional_inputs: dict[str, str]
) -> None:
    # When the settings are read with optional flag inputs
    settings = ActionSettings.from_environment(environment={**REQUIRED_INPUTS, **optional_inputs})

    # Then the preferences carry the flags read from them
    assert settings.preferences == expected


def test_from_environment_when_assignment_options_are_given_then_they_are_listed() -> None:
    # When the settings are read with both assignment options
    settings = ActionSettings.from_environment(
        environment={**REQUIRED_INPUTS, 'INPUT_ASSIGNMENT_OPTIONS': 'ISSUE, PULL_REQUEST'}
    )

    # Then both options are listed
    assert settings.assignment_options == ('ISSUE', 'PULL_REQUEST')


@pytest.mark.parametrize(
    ids=['actor absent', 'repository absent', 'assignees absent', 'token absent', 'assignees blank'],
    argnames=['environment', 'missing'],
    argvalues=[
        ({key: value for key, value in REQUIRED_INPUTS.items() if key != 'GITHUB_ACTOR'}, ('GITHUB_ACTOR',)),
        (
            {key: value for key, value in REQUIRED_INPUTS.items() if key != 'GITHUB_REPOSITORY'},
            ('GITHUB_REPOSITORY',)
        ),
        ({key: value for key, value in REQUIRED_INPUTS.items() if key != 'INPUT_ASSIGNEES'}, ('INPUT_ASSIGNEES',)),
        (
            {key: value for key, value in REQUIRED_INPUTS.items() if key != 'INPUT_GITHUB_TOKEN'},
            ('INPUT_GITHUB_TOKEN',)
        ),
        ({**REQUIRED_INPUTS, 'INPUT_ASSIGNEES': '  '}, ('INPUT_ASSIGNEES',))
    ]
)
def test_from_environment_when_a_required_input_is_missing_then_missing_action_input_names_it(
        missing: tuple[str, ...],
        environment: dict[str, str]
) -> None:
    # Then reading fails because a required input is missing
    with pytest.raises(MissingActionInput) as failure:
        # When the settings are read without that input
        ActionSettings.from_environment(environment=environment)

    # And the failure names that input
    assert failure.value.variables == missing


def test_from_environment_when_every_required_input_is_missing_then_missing_action_input_names_them_all() -> None:
    # Then reading fails because the required inputs are missing
    with pytest.raises(MissingActionInput) as failure:
        # When the settings are read from an empty environment
        ActionSettings.from_environment(environment={})

    # And the failure names every required input at once
    assert failure.value.variables == ('GITHUB_ACTOR', 'GITHUB_REPOSITORY', 'INPUT_ASSIGNEES', 'INPUT_GITHUB_TOKEN')
