from abc import ABCMeta

from edgegraph.syntax.base import BaseSyntax


class BaseExpression(BaseSyntax, metaclass=ABCMeta):
    syntax_type = "expression"
