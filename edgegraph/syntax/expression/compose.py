import enum
import typing as t
from dataclasses import dataclass, field
from functools import lru_cache

from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult


class ReduceType(enum.Enum):
    DISTINCT = "distinct"
    EXISTS = "exists"


@dataclass(frozen=True)
class ReduceExpression(BaseExpression):
    context = "distinct_or_exists_compose"
    type: ReduceType
    side: BaseExpression
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        result = self.side.to_query()

        kwargs = self.variables.copy()
        kwargs.update(result.kwargs)

        return QueryResult(
            query=f"{self.type.value} {result.query}",
            kwargs=kwargs,
        )


@dataclass(frozen=True)
class UnionExpression(BaseExpression):
    context = "union"
    left_side: BaseExpression
    right_side: BaseExpression
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        left_side_result = self.left_side.to_query()
        right_side_result = self.right_side.to_query()

        kwargs = self.variables.copy()
        kwargs.update(left_side_result.kwargs)
        kwargs.update(right_side_result.kwargs)

        return QueryResult(
            query=f"{left_side_result.query} union {right_side_result.query}",
            kwargs=kwargs,
        )


def distinct(side: BaseExpression):
    return ReduceExpression(
        type=ReduceType.DISTINCT,
        side=side,
    )


def exists(side: BaseExpression):
    return ReduceExpression(
        type=ReduceType.EXISTS,
        side=side,
    )


def union(left: BaseExpression, right: BaseExpression):
    return UnionExpression(
        left_side=left,
        right_side=right,
    )
