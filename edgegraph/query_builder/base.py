import abc
from dataclasses import dataclass
from enum import Enum
import typing as t

from edgegraph.errors import ConditionValidationError
from edgegraph.expressions import Expression
from edgegraph.reflections import EdgeGraphField

T = t.TypeVar("T")


class OrderEnum(Enum):
    ASC = "ASC"
    DESC = "DESC"


class EmptyStrategyEnum(Enum):
    FIRST = "FIRST"
    LAST = "LAST"


# Base Query Builder Class. You can extend this class to create custom query builders.
class QueryBuilderBase(t.Generic[T], metaclass=abc.ABCMeta):
    base_cls: t.Type[T]

    def __init__(self, cls: t.Type[T]):
        self.base_cls = cls

    @property
    @abc.abstractmethod
    def query_type(self) -> str:
        pass

    @abc.abstractmethod
    def build(self) -> str:
        pass


@dataclass(frozen=True)
class SelectionField(t.Generic[T]):
    name: str
    type: t.Optional[t.Type[T]] = None
    upper_type_name: t.Optional[str] = None
    expression: t.Optional[Expression] = None
    subquery: t.Optional[QueryBuilderBase] = None


def reference(
    field: t.Union[EdgeGraphField, str],
    expression: t.Optional[Expression] = None,
    subquery: t.Optional[QueryBuilderBase] = None,
) -> SelectionField:
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
        upper_type_name = field.class_name
    else:
        name = field
        typ = None
        upper_type_name = None

    return SelectionField(
        name=name,
        type=typ,
        expression=expression,
        subquery=subquery,
        upper_type_name=upper_type_name,
    )
