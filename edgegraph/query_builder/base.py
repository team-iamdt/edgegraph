import abc
import typing as t
from dataclasses import dataclass
from enum import Enum

from edgegraph.errors import ConditionValidationError
from edgegraph.expressions.base import Expression
from edgegraph.reflections import Configurable, EdgeGraphField
from edgegraph.types import PrimitiveTypes

T = t.TypeVar("T", bound=Configurable)


class QueryBuilderBase(Expression, t.Generic[T], metaclass=abc.ABCMeta):
    def __init__(self, base_type: t.Type[T]):
        self.base_type = base_type


class OrderEnum(Enum):
    ASC = "ASC"
    DESC = "DESC"


class EmptyStrategyEnum(Enum):
    FIRST = "FIRST"
    LAST = "LAST"


class QueryFieldType(Enum):
    EXPRESSION = "EXPRESSION"
    SUBQUERY = "SUBQUERY"
    VALUE = "VALUE"
    NONE = "NONE"


@dataclass(frozen=True)
class BaseQueryField(t.Generic[T]):
    name: str
    query_field_type: QueryFieldType

    value_type: t.Optional[t.Type[T]] = None
    upper_type_name: t.Optional[str] = None

    expression: t.Optional[Expression] = None


@dataclass(frozen=True)
class SelectQueryField(BaseQueryField[T]):
    pass


@dataclass(frozen=True)
class InsertQueryField(BaseQueryField[T]):
    edgedb_type: t.Optional[PrimitiveTypes] = None  # type represented on edgedb
    value: t.Optional[T] = None


def reference(
    field: t.Union[EdgeGraphField, str],
    expression: t.Optional[Expression] = None,
    subquery: t.Optional[Expression] = None,
) -> BaseQueryField:
    if expression is None and subquery is None:
        raise ConditionValidationError(
            f"referencing {field}", "Subquery or Expression is Required"
        )

    if expression is not None and subquery is not None:
        raise ConditionValidationError(
            f"referencing {field}",
            "Subquery and Expression can not referenced with same field",
        )

    if subquery is not None and type(field) is str:
        raise ConditionValidationError(
            f"referencing {field}", "Field must be required as an EdgeGraphField"
        )

    if isinstance(field, EdgeGraphField):
        name = field.name
        value_type = field.type
        upper_type_name = field.base.__name__
    elif type(field) is str:
        name = field
        value_type = None
        upper_type_name = None
    else:
        raise TypeError("Referenced Field can be EdgeGraphField or str")

    if subquery is not None:
        field_type = QueryFieldType.SUBQUERY
        target_expression: t.Optional[Expression] = subquery
    else:
        field_type = QueryFieldType.EXPRESSION
        target_expression = expression

    return BaseQueryField(
        name=name,
        value_type=value_type,
        query_field_type=field_type,
        expression=target_expression,
        upper_type_name=upper_type_name,
    )
