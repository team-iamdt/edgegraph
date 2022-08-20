import typing as t

from edgegraph.errors import ConditionValidationError, QueryContextMissmatchError
from edgegraph.expressions.base import Expression
from edgegraph.query_builder.base import (
    BaseQueryField,
    EmptyStrategyEnum,
    OrderEnum,
    QueryBuilderBase,
    SelectQueryField,
    T,
)
from edgegraph.reflections import EdgeGraphField
from edgegraph.types import QueryResult


class SelectQueryBuilder(QueryBuilderBase[T]):
    query_type = "SELECT"
    _limit: t.Optional[int]
    _offset: t.Optional[int]
    _order_by: t.Optional[t.Tuple[str, OrderEnum]]
    _empty_strategy: t.Optional[EmptyStrategyEnum]
    _fields: t.List[SelectQueryField]
    _filters: t.List[Expression]

    def __init__(self, cls: t.Type[T]):
        super().__init__(cls)
        self._limit = None
        self._offset = None
        self._order_by = None
        self._empty_strategy = None
        self._fields = []
        self._filters = []

    def limit(self, limit: int):
        self._limit = limit
        return self

    def offset(self, offset: int):
        self._offset = offset
        return self

    def order(
        self,
        field: EdgeGraphField[T, t.Any],
        order: OrderEnum,
        empty: t.Optional[EmptyStrategyEnum] = None,
    ):
        field_name = field.name

        # check avilable class fields and queries fields
        available_fields = [
            *self.base_cls.__hints__.keys(),
            *[field.name for field in self._fields],
        ]
        if field_name not in available_fields:
            raise ConditionValidationError(
                f"Field {field_name} does not exist in {self.base_cls}."
            )

        self._order_by = (field_name, order)
        self._empty_strategy = empty
        return self

    def add_field(
        self,
        field: t.Union[EdgeGraphField, SelectQueryField],
    ):
        # First Create SelectField if field is EdgeGraphField
        if isinstance(field, EdgeGraphField):
            selection_field = SelectQueryField(
                name=field.name, type=field.type, upper_type_name=field.base.__name__
            )
        elif isinstance(field, BaseQueryField):
            selection_field = field
        else:
            raise TypeError(
                "SelectQueryField.field can must be EdgeGraphField or SelectQueryField"
            )

        if (
            selection_field.upper_type_name is not None
            and selection_field.upper_type_name != self.base_cls.__name__
        ):
            raise QueryContextMissmatchError(
                selection_field.upper_type_name, self.base_cls
            )

        # Check if field is already in fields
        if selection_field.name in [f.name for f in self._fields]:
            raise ConditionValidationError(
                selection_field.name, "Field already exists."
            )

        # Check if field contains subquery or expression or default field type
        if selection_field.subquery is not None:
            filtered = [
                *filter(
                    lambda f: f[0] == selection_field.name,
                    self.base_cls.__hints__.items(),
                )
            ]

            if len(filtered) == 0:
                raise ConditionValidationError(
                    selection_field.name, "Field does not exist."
                )

            (_, filtered_type) = filtered[0]
            if selection_field.type is None or (
                filtered_type is not selection_field.type
                and issubclass(t.get_args(filtered_type)[0], selection_field.type)
            ):
                raise QueryContextMissmatchError(filtered_type)
        elif selection_field.expression is not None:
            if selection_field.expression.base_cls is not self.base_cls:
                raise QueryContextMissmatchError(
                    self.base_cls, selection_field.expression.base_cls
                )
        else:
            available_fields = self.base_cls.__hints__.keys()
            if selection_field.name not in available_fields:
                raise ConditionValidationError(
                    f"Field {selection_field.name} does not exist in {self.base_cls}."
                )

        self._fields.append(selection_field)
        return self

    def filter(self, expr: Expression):
        if expr in self._filters:
            raise ConditionValidationError(str(expr), "Filter already exists.")
        self._filters.append(expr)
        return self

    def build(self, prefix: str = "") -> QueryResult:
        arguments: t.Dict[str, t.Any] = {}
        (module, model_name) = self.base_cls.get_schema_config()

        self._fields.sort(key=lambda f: f.name)
        self._filters.sort()

        # build selected fields with module/model name
        query = f"select {module}::{model_name} {{\n"
        for field in self._fields:
            keyword_prefix = (
                field.name if len(prefix) == 0 else f"{prefix}__{field.name}"
            )

            if field.subquery is not None and isinstance(
                field.subquery, SelectQueryBuilder
            ):
                subquery_shape = field.subquery.build_shape(keyword_prefix)
                arguments.update(subquery_shape.kwargs)
                query += f"{field.name}: {subquery_shape.query},"
                query += "\n"

            elif field.expression is not None:
                expression = field.expression.build(keyword_prefix)
                arguments.update(expression.kwargs)
                query += f"{field.name}: {expression.kwargs},\n"

            else:
                query += f"{field.name},\n"

        query += "}\n"

        # build filters
        if len(self._filters) > 0:
            query += "filter "

            for idx, filt in enumerate(self._filters):
                filter_prefix = (
                    f"filter_{id(filt)}"
                    if len(prefix) == 0
                    else f"{prefix}__filter_{id(filt)}"
                )

                filter_result = filt.build(filter_prefix)
                arguments.update(filter_result.kwargs)

                query += f"{filter_result.query}"

                if (idx + 1) != len(self._filters):
                    query += " and "

            query += "\n"

        # build order by
        if self._order_by:
            field_name, order = self._order_by
            query += f"order by {field_name} {str(order.value).lower()}"
            if self._empty_strategy:
                query += f" empty {str(self._empty_strategy.value).lower()}"
            query += "\n"

        # build limit and offset
        if self._offset is not None:
            query += f"offset {self._offset}"
            query += "\n"

        if self._limit is not None:
            query += f"limit {self._limit}"
            query += "\n"

        return QueryResult(query, arguments)

    def build_shape(self, prefix: str = "") -> QueryResult:
        arguments: t.Dict[str, t.Any] = {}
        query = "{\n"
        for field in self._fields:
            field_prefix = f"{prefix}__{field.name}" if len(prefix) > 0 else field.name

            if field.subquery is not None and isinstance(
                field.subquery, SelectQueryBuilder
            ):
                subquery = field.subquery.build_shape(field_prefix)
                arguments.update(subquery.kwargs)
                query += f"{field.name}: {subquery.query},"
                query += "\n"

            elif field.expression is not None:
                expression = field.expression.build(field_prefix)
                arguments.update(expression.kwargs)
                query += f"{field.name}: {expression.query},\n"

            else:
                query += f"{field.name},\n"

        query += "}"

        return QueryResult(query, arguments)
