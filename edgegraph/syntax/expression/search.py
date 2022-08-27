import enum
import typing as t
from dataclasses import dataclass, field
from functools import lru_cache

from edgegraph.errors import ExpressionError
from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult


class InType(enum.Enum):
    IN = "in"
    NOT_IN = "not in"


class LikeType(enum.Enum):
    LIKE = "like"
    ILIKE = "ilike"
    NOT_LIKE = "not like"
    NOT_ILIKE = "not ilike"


@dataclass(frozen=True)
class InExpression(BaseException):
    context = "in"
    type: InType
    target: BaseExpression
    compare: t.Union[t.Iterable, BaseExpression]
    edgedb_type: t.Optional[str] = None
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        kwargs = self.variables.copy()

        target_result = self.target.to_query()
        if isinstance(self.compare, BaseExpression):
            compare_result = self.compare.to_query()
            compare_query = compare_result.query
            compare_args = compare_result.kwargs
        else:
            if self.edgedb_type is None:
                message = "IN expression must be provide EdgeDB type when target is not expression."
                raise ExpressionError(
                    self.context,
                    message,
                )

            variable_name = f"{self.context}_{id(self)}"
            compare_query = f"<array<{self.edgedb_type}>>${variable_name}"
            compare_args = {
                variable_name: self.compare,
            }

        kwargs.update(target_result.kwargs)
        kwargs.update(compare_args)

        query = f"{target_result.query} {self.type.value} {compare_query}"
        return QueryResult(
            query=query,
            kwargs=kwargs,
        )


@dataclass(frozen=True)
class LikeExpression(BaseExpression):
    context = "like"
    type: LikeType
    target: BaseExpression
    compare: t.Union[str, BaseExpression]
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        kwargs = self.variables.copy()
        target_result = self.target.to_query()

        if isinstance(self.compare, str):
            variable_name = f"{self.context}_{id(self)}"
            compare_query = f"<str>${variable_name}"
            compare_args: t.Dict[str, t.Any] = {
                variable_name: self.compare,
            }
        else:
            compare_result = self.compare.to_query()
            compare_query = compare_result.query
            compare_args = compare_result.kwargs

        kwargs.update(target_result.kwargs)
        kwargs.update(compare_args)

        query = f"{target_result.query} {self.type.value} {compare_query}"
        return QueryResult(
            query=query,
            kwargs=kwargs,
        )


def in_expr(
    target: BaseExpression,
    compare: t.Union[t.Iterable, BaseExpression],
    edgedb_type: t.Optional[str] = None,
):
    return InExpression(
        type=InType.IN,
        target=target,
        compare=compare,
        edgedb_type=edgedb_type,
    )


def not_in_expr(
    target: BaseExpression,
    compare: t.Union[t.Iterable, BaseExpression],
    edgedb_type: t.Optional[str] = None,
):
    return InExpression(
        type=InType.NOT_IN,
        target=target,
        compare=compare,
        edgedb_type=edgedb_type,
    )


def like(
    target: BaseExpression,
    compare: t.Union[str, BaseExpression],
):
    return LikeExpression(
        type=LikeType.LIKE,
        target=target,
        compare=compare,
    )


def not_like(
    target: BaseExpression,
    compare: t.Union[str, BaseExpression],
):
    return LikeExpression(
        type=LikeType.NOT_LIKE,
        target=target,
        compare=compare,
    )


def ilike(
    target: BaseExpression,
    compare: t.Union[str, BaseExpression],
):
    return LikeExpression(
        type=LikeType.ILIKE,
        target=target,
        compare=compare,
    )


def not_ilike(
    target: BaseExpression,
    compare: t.Union[str, BaseExpression],
):
    return LikeExpression(
        type=LikeType.NOT_ILIKE,
        target=target,
        compare=compare,
    )
