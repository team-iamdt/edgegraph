import abc

from edgegraph.types import QueryResult


class Expression(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def type(self) -> str:
        pass

    @abc.abstractmethod
    def build(self, prefix: str = "") -> QueryResult:
        pass
