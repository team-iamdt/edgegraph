import abc
from enum import Enum
import typing as t

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
