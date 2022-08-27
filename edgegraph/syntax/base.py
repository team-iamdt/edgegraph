import typing as t
from abc import ABCMeta, abstractmethod

from edgegraph.types import QueryResult


class BaseSyntax(metaclass=ABCMeta):
    syntax_type: t.ClassVar[str]
    context: t.ClassVar[str]
    variables: t.Dict[str, t.Any]

    @abstractmethod
    def to_query(self) -> QueryResult:
        pass
