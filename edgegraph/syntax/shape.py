import typing as t
from dataclasses import dataclass, field
from enum import Enum

from edgegraph.errors import ConditionValidationError
from edgegraph.reflections import EdgeGraphProperty
from edgegraph.syntax.base import BaseSyntax
from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.syntax.query.base import BaseQuery
from edgegraph.types import QueryResult

T = t.TypeVar("T")
V = t.TypeVar("V")

PropertyDefinition: t.TypeAlias = t.Union[EdgeGraphProperty[T, V], str]
# here can be subquery, shape, expressions, value
ValueType: t.TypeAlias = t.Optional[t.Union[BaseSyntax, V]]


class ShapePointerType(Enum):
    NONE = ""
    LINKED = ":"
    ASSIGN = ":="
    APPEND = "+="
    REMOVE = "-="


class ShapeQueryType(Enum):
    UPSERT = "UPSERT"
    SELECT = "SELECT"


@dataclass(frozen=True)
class ShapeItems(t.Generic[T, V]):
    property: PropertyDefinition
    type: ShapePointerType
    value: ValueType
    edgedb_type: t.Optional[str] = None


# T means shape root's type
@dataclass(frozen=True)
class Shape(BaseSyntax, t.Generic[T, V]):
    syntax_type = "shape"
    shape_query_type: ShapeQueryType
    items: t.List[ShapeItems[T, V]]
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    def _get_available_pointers(self):
        if self.shape_query_type == ShapeQueryType.UPSERT:
            return [
                ShapePointerType.LINKED,
                ShapePointerType.ASSIGN,
                ShapePointerType.APPEND,
                ShapePointerType.REMOVE,
            ]
        else:
            return [
                ShapePointerType.NONE,
                ShapePointerType.LINKED,
                ShapePointerType.ASSIGN,  # for custom fields only
            ]

    def to_query(self) -> QueryResult:
        query = "{\n"
        kwargs = self.variables.copy()

        for item in self.items:
            # Base Validations
            if item.type not in self._get_available_pointers():
                raise ConditionValidationError(
                    condition=str(item),
                    message=f"{item.type.name} cannot be in {self.shape_query_type}.",
                )

            if (
                self.shape_query_type == ShapeQueryType.SELECT
                and item.type == ShapePointerType.ASSIGN
                and not isinstance(item.property, str)
            ):
                raise ConditionValidationError(
                    condition=str(item),
                    message=f"In {self.shape_query_type}, Assignment can be used for custom property only.",
                )

            property_name = (
                item.property.name
                if isinstance(item.property, EdgeGraphProperty)
                else item.property
            )

            if isinstance(item.value, Shape):
                if item.type != ShapePointerType.LINKED:
                    raise ConditionValidationError(
                        condition=str(item),
                        message="Shape Value can be used with ShapePointerType.LINKED.",
                    )

                inner_shape = item.value.to_query()
                query += f"{property_name} {item.type.value} {inner_shape.query},\n"
                kwargs.update(inner_shape.kwargs)

            elif isinstance(item.value, BaseExpression):
                if item.type == ShapePointerType.NONE:
                    raise ConditionValidationError(
                        condition=str(item),
                        message="Expression Value cannot be used with ShapePointerType.NONE.",
                    )

                inner_expression = item.value.to_query()
                query += (
                    f"{property_name} {item.type.value} {inner_expression.query},\n"
                )
                kwargs.update(inner_expression.kwargs)

            elif isinstance(item.value, BaseQuery):
                if item.type in [ShapePointerType.NONE, ShapePointerType.LINKED]:
                    raise ConditionValidationError(
                        condition=str(item),
                        message="Sub Query cannot be used with ShapePointerType.NONE or LINKED.",
                    )

                subquery = item.value.to_query()
                query += f"{property_name} {item.type.value} ({subquery}),\n"
                kwargs.update(subquery.kwargs)

            else:
                if item.edgedb_type is None:
                    raise ConditionValidationError(
                        condition=str(item),
                        message="Raw Value must be provide EdgeDB Type.",
                    )

                if item.type != ShapePointerType.ASSIGN:
                    raise ConditionValidationError(
                        condition=str(item),
                        message="Raw Value must be used with ShapePointerType.ASSIGN",
                    )

                variable_name = f"{property_name}_{id(item)}"
                query += f"{property_name} {item.type.value} <{item.edgedb_type}>${variable_name},\n"
                kwargs[variable_name] = item.value

        query += "}"

        return QueryResult(
            query=query,
            kwargs=kwargs,
        )
