import pytest

from src.application.domain.exceptions.login_cannot_be_empty import LoginCannotBeEmpty
from src.application.domain.models.commons.login import Login


@pytest.mark.parametrize(
    ids=['empty', 'blank'],
    argnames=['value'],
    argvalues=[('',), ('   ',)]
)
def test_login_when_value_is_blank_then_login_cannot_be_empty_is_raised(value: str) -> None:
    # Then the login is refused because it names nobody
    with pytest.raises(LoginCannotBeEmpty):
        # When a login is created from a blank value
        Login(value=value)


@pytest.mark.parametrize(
    ids=['bot account', 'person', 'bot marker inside the login'],
    argnames=['value', 'expected'],
    argvalues=[('dependabot[bot]', True), ('octocat', False), ('octo[bot]cat', False)]
)
def test_is_bot_when_a_login_is_inspected_then_only_the_bot_suffix_marks_a_bot(value: str, expected: bool) -> None:
    # When the login is asked whether it names a bot
    is_bot = Login(value=value).is_bot()

    # Then only a login ending with the bot suffix names a bot
    assert is_bot is expected
