from abc import ABCMeta

from edgegraph.syntax.base import BaseSyntax


class BaseQuery(BaseSyntax, metaclass=ABCMeta):
    syntax_type = "query"
