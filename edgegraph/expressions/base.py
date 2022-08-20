import abc
import typing as t

from edgegraph.types import QueryResult

T = t.TypeVar("T")


class Expression(t.Generic[T], metaclass=abc.ABCMeta):
    base_cls: t.Type[T]

    @abc.abstractmethod
    def build(self, prefix: str = "") -> QueryResult:
        pass
