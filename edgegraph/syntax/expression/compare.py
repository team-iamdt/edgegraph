import enum
import typing as t
from dataclasses import dataclass, field
from functools import lru_cache

from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult


class CompareType(enum.Enum):
    EQ = "="
    NEQ = "!="
    EEQ = "?="
    NEEQ = "?!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="


@dataclass(frozen=True)
class CompareExpression(BaseExpression):
    context = "compare"
    compare_type: CompareType
    left_side: BaseExpression
    right_side: BaseExpression
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        left_result = self.left_side.to_query()
        right_result = self.right_side.to_query()

        kwargs = self.variables.copy()
        kwargs.update(left_result.kwargs)
        kwargs.update(right_result.kwargs)

        query = (
            f"{left_result.query} "
            f"{self.compare_type.value} "
            f"{right_result.query}"
        )

        return QueryResult(
            query=query,
            kwargs=kwargs,
        )


def equals(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.EQ,
        left_side=left,
        right_side=right,
    )


def not_equals(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.EQ,
        left_side=left,
        right_side=right,
    )


def empty_equals(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.EEQ,
        left_side=left,
        right_side=right,
    )


def not_empty_equals(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.NEQ,
        left_side=left,
        right_side=right,
    )


def greater_than(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.GT,
        left_side=left,
        right_side=right,
    )


def greater_than_equal(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.GTE,
        left_side=left,
        right_side=right,
    )


def less_than(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.LT,
        left_side=left,
        right_side=right,
    )


def less_than_equal(left: BaseExpression, right: BaseExpression):
    return CompareExpression(
        compare_type=CompareType.LTE,
        left_side=left,
        right_side=right,
    )
