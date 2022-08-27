from abc import ABCMeta
from dataclasses import dataclass

from edgegraph.syntax.base import BaseSyntax


# https://github.com/python/mypy/pull/13398
@dataclass(frozen=True, init=False)  # type: ignore
class BaseQuery(BaseSyntax, metaclass=ABCMeta):
    syntax_type = "query"
