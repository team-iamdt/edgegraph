import typing as t
from dataclasses import dataclass, field
from functools import lru_cache

from edgegraph.errors import ExpressionError
from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult


@dataclass(frozen=True)
class CoalesceExpression(BaseExpression):
    context = "coalesce"
    side: BaseExpression
    coalesce_side: t.Union[BaseExpression, t.Any]
    coalesce_type: t.Optional[str] = None
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        result = self.side.to_query()

        if isinstance(self.coalesce_side, BaseExpression):
            coalesce_result = self.coalesce_side.to_query()
            coalesce_query = coalesce_result.query
            coalesce_kwargs = coalesce_result.kwargs
        else:
            if self.coalesce_type is None:
                raise ExpressionError(
                    self.context,
                    "coalesce_type must be provided when coalesce_side is not expression.",
                )

            variable_name = f"{self.context}_{id(self)}"
            coalesce_query = f"<{self.coalesce_type}>${variable_name}"
            coalesce_kwargs = {
                variable_name: self.coalesce_side,
            }

        kwargs = self.variables.copy()
        kwargs.update(result.kwargs)
        kwargs.update(coalesce_kwargs)

        query = f"{result} ?? {coalesce_query}"
        return QueryResult(
            query=query,
            kwargs=kwargs,
        )


def coalesce(
    side: BaseExpression,
    coalesce_side: t.Union[BaseExpression, t.Any],
    coalesce_type: t.Optional[str] = None,
):
    return CoalesceExpression(
        side=side,
        coalesce_side=coalesce_side,
        coalesce_type=coalesce_type,
    )
