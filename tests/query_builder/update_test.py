import asyncio
import os
from textwrap import dedent

import pendulum
import pytest

import tests.models as m
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


def test_valid_update_filter_query_with_edgeql():
    MemoModel = m.MemoModel

    memo_update = (
        MemoModel.update()
        .add_filter(
            SideExpression(
                equation="LIKE",
                origin=field(MemoModel.content),
                target="%테스트%",
                target_type=PrimitiveTypes.STRING,
            )
        )
        .add_field(field(MemoModel.deleted), db_type=PrimitiveTypes.BOOL, value=True)
        .add_field(
            field(MemoModel.deleted_at),
            db_type=PrimitiveTypes.DATETIME,
            value=pendulum.now(),
        )
        .build()
    )

    assert (
        dedent(
            """
            set {
            deleted := <bool>$deleted,
            deleted_at := <datetime>$deleted_at,
            }
        """
        )[1:]
        in memo_update.query
    )

    assert "update default::Memo\n" in memo_update.query
    assert "filter .content LIKE <str>$filter_" in memo_update.query

    assert "deleted" in memo_update.kwargs
    assert "deleted_at" in memo_update.kwargs


def test_valid_update_subquery_query_with_edgeql():
    MemoModel = m.MemoModel

    memo_select_query = MemoModel.select(
        [
            field(MemoModel.id),
            field(MemoModel.content),
            field(MemoModel.deleted),
            field(MemoModel.deleted_at),
        ]
    ).add_filter(
        SideExpression(
            equation="LIKE",
            origin=field(MemoModel.content),
            target="%테스트%",
            target_type=PrimitiveTypes.STRING,
        )
    )

    memo_update_query = (
        MemoModel.update()
        .set_target(memo_select_query)
        .add_field(field(MemoModel.deleted), db_type=PrimitiveTypes.BOOL, value=True)
        .add_field(
            field(MemoModel.deleted_at),
            db_type=PrimitiveTypes.DATETIME,
            value=pendulum.now(),
        )
        .build()
    )

    assert memo_update_query.query.startswith(
        dedent(
            """
                update (
                select default::Memo {
                content,
                deleted,
                deleted_at,
                id,
                }
                filter .content LIKE <str>$target__filter_
            """
        )[1:-1]
    )

    assert memo_update_query.query.endswith(
        dedent(
            """
                )
                set {
                deleted := <bool>$deleted,
                deleted_at := <datetime>$deleted_at,
                }
            """
        )[1:]
    )
