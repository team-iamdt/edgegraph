import asyncio
import os
from textwrap import dedent

import pytest

import tests.models as m
from edgegraph.errors import QueryContextMissmatchError
from edgegraph.query_builder.base import EmptyStrategyEnum, OrderEnum, reference


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def edgedb_dsn():
    dsn = os.getenv("EDGEDB_DSN")
    if not dsn:
        pytest.skip("Cannot test this test without EDGEDB_DSN environment variable.")

    return dsn


def test_valid_select_query_with_edgeql():
    UserModel = m.UserModel
    MemoModel = m.MemoModel

    user_subquery = (
        UserModel.select().field(UserModel.fields.id).field(UserModel.fields.name)
    )

    memo_select = (
        MemoModel.select()
        .field(MemoModel.fields.id)
        .field(MemoModel.fields.content)
        .field(MemoModel.fields.created_at)
        .field(reference(MemoModel.fields.created_by, subquery=user_subquery))
        .field(reference(MemoModel.fields.accessable_users, subquery=user_subquery))
        .limit(10)
        .offset(0)
        .order(MemoModel.fields.created_at, OrderEnum.DESC, EmptyStrategyEnum.LAST)
        .build()
    )

    check_query = """
        with module default select Memo {
        id,
        content,
        created_at,
        created_by: {
        id,
        name,
        },
        accessable_users: {
        id,
        name,
        },
        }
        order by created_at desc empty last
        offset 0
        limit 10
        ;
    """

    # Dedent check is might be remove first, and last line break.
    assert dedent(memo_select) == dedent(check_query)[1:-1]


def test_invalid_fields_in_select_query():
    UserModel = m.UserModel
    MemoModel = m.MemoModel

    user_subquery = (
        UserModel.select().field(UserModel.fields.id).field(UserModel.fields.name)
    )

    with pytest.raises(QueryContextMissmatchError):
        (
            MemoModel.select()
            .field(MemoModel.fields.id)
            .field(MemoModel.fields.content)
            .field(UserModel.fields.created_at)
            .field(reference(MemoModel.fields.created_by, subquery=user_subquery))
            .field(reference(MemoModel.fields.accessable_users, subquery=user_subquery))
            .limit(10)
            .offset(0)
            .order(MemoModel.fields.created_at, OrderEnum.DESC, EmptyStrategyEnum.LAST)
            .build()
        )
