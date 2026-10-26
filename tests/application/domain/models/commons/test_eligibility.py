import pytest

from src.application.domain.models.commons.eligibility import Eligibility
from src.application.domain.models.commons.login import Login


@pytest.mark.parametrize(
    ids=[
        'bot skipped',
        'bot kept when bots are not skipped',
        'person kept while bots are skipped',
        'draft skipped',
        'draft kept when drafts are not skipped',
        'ready item kept while drafts are skipped'
    ],
    argnames=['skip_bots', 'skip_drafts', 'author', 'draft', 'expected'],
    argvalues=[
        (True, False, Login(value='dependabot[bot]'), False, True),
        (False, False, Login(value='dependabot[bot]'), False, False),
        (True, False, Login(value='carol'), False, False),
        (False, True, Login(value='carol'), True, True),
        (False, False, Login(value='carol'), True, False),
        (False, True, Login(value='carol'), False, False)
    ]
)
def test_excludes_when_an_item_is_judged_then_only_a_skipped_kind_is_excluded(
        draft: bool,
        author: Login,
        expected: bool,
        skip_bots: bool,
        skip_drafts: bool
) -> None:
    # When an item is judged by its author and its draft flag
    excluded = Eligibility(skip_bots=skip_bots, skip_drafts=skip_drafts).excludes(author=author, draft=draft)

    # Then the item is excluded only when its kind is skipped
    assert excluded is expected
