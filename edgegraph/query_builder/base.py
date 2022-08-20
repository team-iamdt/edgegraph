import abc
import typing as t
from dataclasses import dataclass
from enum import Enum

from edgegraph.errors import ConditionValidationError
from edgegraph.expressions.base import Expression
from edgegraph.reflections import Configurable, EdgeGraphField
from edgegraph.types import PrimitiveTypes, QueryResult

T = t.TypeVar("T", bound=Configurable)


class OrderEnum(Enum):
    ASC = "ASC"
    DESC = "DESC"


class EmptyStrategyEnum(Enum):
    FIRST = "FIRST"
    LAST = "LAST"


# Base Query Builder Class. You can extend this class to create custom query builders.
class QueryBuilderBase(t.Generic[T], metaclass=abc.ABCMeta):
    def __init__(self, cls: t.Type[T]):
        self.base_cls = cls

    @property
    @abc.abstractmethod
    def query_type(self) -> str:
        pass

    @abc.abstractmethod
    def build(self, prefix: str = "") -> QueryResult:
        pass


@dataclass(frozen=True)
class BaseQueryField(t.Generic[T]):
    name: str
    type: t.Optional[t.Type[T]] = None
    upper_type_name: t.Optional[str] = None
    expression: t.Optional[Expression] = None
    subquery: t.Optional[QueryBuilderBase] = None


@dataclass(frozen=True)
class SelectQueryField(BaseQueryField[T]):
    pass


@dataclass(frozen=True)
class InsertQueryField(BaseQueryField[T]):
    value_type: t.Optional[PrimitiveTypes] = None  # type represented on edgedb
    value: t.Optional[T] = None


def reference(
    field: t.Union[EdgeGraphField, str],
    expression: t.Optional[Expression] = None,
    subquery: t.Optional[QueryBuilderBase] = None,
) -> BaseQueryField:
    if expression is None and subquery is None:
        raise ConditionValidationError(
            f"referencing {field}", "Subquery or Expression is Required"
        )

    if subquery is not None and type(field) is str:
        raise ConditionValidationError(
            f"referencing {field}", "Field must be required as an EdgeGraphField"
        )

    if isinstance(field, EdgeGraphField):
        name = field.name
        typ = field.type
        upper_type_name = field.base.__name__
    elif type(field) is str:
        name = field
        typ = None
        upper_type_name = None
    else:
        raise TypeError("Referenced Field can be EdgeGraphField or str")

    return BaseQueryField(
        name=name,
        type=typ,
        expression=expression,
        subquery=subquery,
        upper_type_name=upper_type_name,
    )
