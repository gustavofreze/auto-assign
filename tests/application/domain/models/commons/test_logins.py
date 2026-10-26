from src.application.domain.models.commons.login import Login
from src.application.domain.models.commons.logins import Logins


def test_from_raw_when_values_are_given_then_returns_one_login_per_value_in_order() -> None:
    # When logins are created from two values
    logins = Logins.from_raw(values=('bob', 'alice'))

    # Then each value becomes a login, in the given order
    assert tuple(logins) == (Login(value='bob'), Login(value='alice'))


def test_empty_when_created_then_holds_no_login() -> None:
    # When an empty collection is created
    logins = Logins.empty()

    # Then it holds no login
    assert len(logins) == 0


def test_contains_when_a_login_is_held_then_it_is_found() -> None:
    # Given logins holding alice
    logins = Logins.from_raw(values=('alice',))

    # When alice and bob are looked up
    found = (Login(value='alice') in logins, Login(value='bob') in logins)

    # Then only alice is found
    assert found == (True, False)


def test_without_when_a_login_is_held_then_every_other_login_is_kept_in_order() -> None:
    # Given logins holding bob, octocat, and alice
    logins = Logins.from_raw(values=('bob', 'octocat', 'alice'))

    # When octocat is left out
    remaining = logins.without(login=Login(value='octocat'))

    # Then bob and alice remain, in their order
    assert remaining == Logins.from_raw(values=('bob', 'alice'))


def test_shared_with_when_some_logins_are_shared_then_returns_them_in_this_order() -> None:
    # Given requested logins and the logins of the repository members
    requested = Logins.from_raw(values=('bob', 'stranger', 'alice'))
    members = Logins.from_raw(values=('alice', 'bob'))

    # When the requested logins are matched against the members
    shared = requested.shared_with(other=members)

    # Then only the shared logins remain, in the requested order
    assert shared == Logins.from_raw(values=('bob', 'alice'))


def test_including_when_other_logins_are_new_then_they_are_appended_in_order() -> None:
    # Given logins holding bob
    logins = Logins.from_raw(values=('bob',))

    # When carol and alice are included
    included = logins.including(other=Logins.from_raw(values=('carol', 'alice')))

    # Then carol and alice follow bob, in the given order
    assert included == Logins.from_raw(values=('bob', 'carol', 'alice'))


def test_including_when_other_logins_are_already_held_then_they_are_not_repeated() -> None:
    # Given logins holding bob and alice
    logins = Logins.from_raw(values=('bob', 'alice'))

    # When alice and carol are included
    included = logins.including(other=Logins.from_raw(values=('alice', 'carol')))

    # Then alice is kept once, in its original place, and carol is appended
    assert included == Logins.from_raw(values=('bob', 'alice', 'carol'))
