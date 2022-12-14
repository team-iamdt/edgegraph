import asyncio
import os
import uuid
from textwrap import dedent

import pendulum
import pytest

import tests.models as m
from edgegraph.errors import ConditionValidationError
from edgegraph.expressions.side import SideExpression
from edgegraph.reflections import field
from edgegraph.types import PrimitiveTypes


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


def test_valid_insert_query_with_edgeql():
    MemoModel = m.MemoModel

    date = pendulum.now()
    memo_insert = (
        MemoModel.insert()
        .add_field(
            field(MemoModel.content),
            value="Some Memo",
            db_type=PrimitiveTypes.STRING,
        )
        .add_field(field(MemoModel.created_at), date, db_type=PrimitiveTypes.DATETIME)
        .add_field(field(MemoModel.updated_at), date, db_type=PrimitiveTypes.DATETIME)
        .build()
    )

    # check subquery
    assert memo_insert.kwargs == {
        "content": "Some Memo",
        "created_at": date,
        "updated_at": date,
    }

    assert (
        dedent(
            """
                insert default::Memo {
                content := <str>$content,
                created_at := <datetime>$created_at,
                updated_at := <datetime>$updated_at,
                }
            """
        )[1:]
        == dedent(memo_insert.query)
    )


def test_valid_insert_query_with_subquery_with_edgeql():
    UserModel = m.UserModel
    MemoModel = m.MemoModel

    user_subquery = UserModel.select(
        [field(UserModel.id), field(UserModel.name)]
    ).add_filter(
        SideExpression(
            equation="=",
            origin=field(UserModel.id),
            target=uuid.UUID("7acf23a6-1c86-11ed-9e22-729bc6601436"),
            target_type=PrimitiveTypes.UUID,
        )
    )

    date = pendulum.now()
    memo_insert = (
        MemoModel.insert()
        .add_field(
            field(MemoModel.content),
            value="Some Memo",
            db_type=PrimitiveTypes.STRING,
        )
        .add_field(field(MemoModel.created_by), subquery=user_subquery)
        .add_field(field(MemoModel.created_at), date, db_type=PrimitiveTypes.DATETIME)
        .add_field(field(MemoModel.updated_at), date, db_type=PrimitiveTypes.DATETIME)
        .build()
    )

    # check subquery value contains
    result = False
    for key in memo_insert.kwargs.keys():
        if key.startswith("created_by__filter_") and "__equation_" in key:
            result = True

    assert result


def test_invalid_insert_query_parameter():
    UserModel = m.UserModel
    MemoModel = m.MemoModel

    user_subquery = UserModel.select().add_filter(
        SideExpression(
            equation="=",
            origin=field(UserModel.id),
            target=uuid.UUID("7acf23a6-1c86-11ed-9e22-729bc6601436"),
            target_type=PrimitiveTypes.UUID,
        )
    )

    with pytest.raises(ConditionValidationError):
        (
            MemoModel.insert()
            .add_field(
                field(MemoModel.content),
                value="Some Memo",
                db_type=PrimitiveTypes.STRING,
            )
            .add_field(field(MemoModel.created_by), subquery=user_subquery)
            .add_field(field(MemoModel.created_at), pendulum.now())
            .add_field(field(MemoModel.updated_at), pendulum.now())
            .build()
        )
