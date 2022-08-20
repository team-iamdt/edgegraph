import typing as t

from edgegraph.errors import ExpressionError
from edgegraph.expressions.base import Expression
from edgegraph.reflections import EdgeGraphField
from edgegraph.types import PrimitiveTypes, QueryResult

V = t.TypeVar("V")


class SideExpression(Expression, t.Generic[V]):
    context = "equation"
    _equation: str
    _origin: t.Union[V, EdgeGraphField, Expression]
    _target: t.Union[V, Expression]
    _origin_type: t.Optional[PrimitiveTypes] = None
    _target_type: t.Optional[PrimitiveTypes] = None

    def __init__(
        self,
        equation: str,
        origin: t.Union[EdgeGraphField, Expression, V],
        target: t.Union[Expression, V],
        origin_type: t.Optional[PrimitiveTypes] = None,
        target_type: t.Optional[PrimitiveTypes] = None,
    ):
        self._equation = equation
        self._origin = origin
        self._target = target
        self._origin_type = origin_type
        self._target_type = target_type

    def build(self, prefix: str = "") -> QueryResult:
        result_dict: t.Dict[str, t.Any] = dict()

        if not (
            isinstance(self._origin, EdgeGraphField)
            or isinstance(self._origin, Expression)
        ):
            if self._origin_type is None:
                raise ExpressionError(
                    self.context, f"Origin type is not defined for {self._origin}"
                )

            origin_key = f"{self.context}_{id(self._origin)}"
            origin_key = f"{prefix}__{origin_key}" if len(prefix) > 0 else origin_key
            origin_query = f"<{self._origin_type.name}>${origin_key}"
            result_dict[origin_key] = self._origin
        elif isinstance(self._origin, EdgeGraphField):
            origin_query = f".{self._origin.name}"
        else:
            (origin_query, update_dict) = self._origin.build()
            result_dict.update(update_dict)
            origin_query = f"({origin_query})"

        if not isinstance(self._target, Expression):
            if self._target_type is None:
                raise ExpressionError(
                    self.context, f"Target type is not defined for {self._target}"
                )

            target_key = f"{self.context}_{id(self._target)}"
            target_key = f"{prefix}__{target_key}" if len(prefix) > 0 else target_key
            target_query = f"<{self._target_type.value}>${target_key}"
            result_dict[target_key] = self._target
        else:
            (target_query, update_dict) = self._target.build()
            result_dict.update(update_dict)
            target_query = f"({target_query})"

        result_query = f"{origin_query} {self._equation} {target_query}"
        return QueryResult(result_query, result_dict)
