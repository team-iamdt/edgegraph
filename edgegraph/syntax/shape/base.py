from abc import ABCMeta

from edgegraph.syntax.base import BaseSyntax


class BaseShape(BaseSyntax, metaclass=ABCMeta):
    syntax_type = "shape"
