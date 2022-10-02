import enum
import typing as t
from dataclasses import dataclass, field

from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult


class MultipleConditionType(enum.Enum):
    AND = "and"
    OR = "or"


@dataclass(frozen=True)
class AndOrExpression(BaseExpression):
    context = "and_or_conditional"
    condition: MultipleConditionType
    left_side: BaseExpression
    right_side: BaseExpression
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    def to_query(self) -> QueryResult:
        left_result = self.left_side.to_query()
        right_result = self.right_side.to_query()

        kwargs = self.variables.copy()
        kwargs.update(left_result.kwargs)
        kwargs.update(right_result.kwargs)

        query = (
            f"{left_result.query} " f"{self.condition.value} " f"{right_result.query}"
        )

        return QueryResult(
            query=query,
            kwargs=kwargs,
        )


@dataclass(frozen=True)
class NotExpression(BaseExpression):
    context = "not_conditional"
    side: BaseExpression
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    def to_query(self) -> QueryResult:
        side_result = self.side.to_query()

        kwargs = self.variables.copy()
        kwargs.update(side_result.kwargs)

        query = f"not {side_result.query}"

        return QueryResult(
            query=query,
            kwargs=kwargs,
        )


def and_expr(left: BaseExpression, right: BaseExpression):
    return AndOrExpression(
        condition=MultipleConditionType.AND,
        left_side=left,
        right_side=right,
    )


def or_expr(left: BaseExpression, right: BaseExpression):
    return AndOrExpression(
        condition=MultipleConditionType.OR,
        left_side=left,
        right_side=right,
    )


def not_expr(side: BaseExpression):
    return NotExpression(
        side=side,
    )
