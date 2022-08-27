import typing as t
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from edgegraph.types import QueryResult


# I used type ignore caused by https://github.com/python/mypy/pull/13398
# still not released in library.
@dataclass(frozen=True, init=False)  # type: ignore
class BaseSyntax(metaclass=ABCMeta):
    syntax_type: t.ClassVar[str]
    context: t.ClassVar[str]
    variables: t.Dict[str, t.Any]

    @abstractmethod
    def to_query(self) -> QueryResult:
        pass
