import typing as t
from dataclasses import dataclass, field
from functools import lru_cache

from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult


@dataclass(frozen=True)
class ScopeExpression(BaseExpression):
    context = "scope"
    side: BaseExpression
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        side_result = self.side.to_query()

        return QueryResult(
            query=f"({side_result.query})",
            kwargs=side_result.kwargs,
        )


def scope(expr: BaseExpression):
    return ScopeExpression(
        side=expr,
    )
