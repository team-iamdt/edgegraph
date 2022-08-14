import typing as t

from edgegraph.errors import ConditionValidationError, QueryContextMissmatchingError
from edgegraph.expressions import Expression
from edgegraph.query_builder.base import (
    EmptyStrategyEnum,
    OrderEnum,
    QueryBuilderBase,
    T,
)


Field: t.TypeAlias = t.Tuple[str, t.Any]
ExpressionField: t.TypeAlias = t.Tuple[str, Expression]


class SelectQueryBuilder(QueryBuilderBase):
    query_type = "SELECT"
    _limit: t.Optional[int]
    _offset: t.Optional[int]
    _order_by: t.Optional[t.Tuple[str, OrderEnum]]
    _empty_strategy: t.Optional[EmptyStrategyEnum]
    _fields: t.List[t.Union[Field, ExpressionField, t.Tuple[str, "SelectQueryBuilder"]]]
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
        field: Field,
        order: OrderEnum,
        empty: t.Optional[EmptyStrategyEnum] = None,
    ):
        field_name, field_value = field

        # check avilable class fields and queries fields
        available_fields = [
            *self.base_cls.fields().__fields__.keys(),
            *[field[0] for field in self._fields],
        ]
        if field_name not in available_fields:
            raise ConditionValidationError(
                f"Field {field_name} does not exist in {self.base_cls}."
            )

        self._order_by = (field_name, order)
        self._empty_strategy = empty
        return self

    def field(
        self, field: t.Union[Field, ExpressionField, t.Tuple[str, "SelectQueryBuilder"]]
    ):
        field_name, field_value = field

        if field_name in [f[0] for f in self._fields]:
            raise ConditionValidationError(field_name, "Field already exists.")

        if issubclass(type(field_value), Expression):
            # here is logic for expression.
            if field_value.base_cls is not self.base_cls:
                raise QueryContextMissmatchingError(self.base_cls, field_value.base_cls)
        elif type(field_value) is SelectQueryBuilder:
            # here is logic for subquery.
            filtered = list(
                filter(
                    lambda f: f[0] == field_name,
                    self.base_cls.fields().__fields__.items(),
                )
            )
            if len(filtered) == 0:
                raise ConditionValidationError(field_name, "Field does not exist.")

            (_, filtered_type) = filtered[0]
            if not (
                filtered_type is field_value.base_cls
                or issubclass(t.get_args(filtered_type)[0], field_value.base_cls)
            ):
                raise QueryContextMissmatchingError(filtered_type, field_value.base_cls)
        else:
            # here is logic for field
            available_fields = self.base_cls.fields().__fields__.keys()
            if field_name not in available_fields:
                raise ConditionValidationError(
                    f"Field {field_name} does not exist in {self.base_cls}."
                )

        self._fields.append(field)
        return self

    def filter(self, expr: Expression):
        if expr in self._filters:
            raise ConditionValidationError(str(expr), "Filter already exists.")
        self._filters.append(expr)
        return self

    def build(self) -> str:
        model_name = (
            self.base_cls.Config.name
            if self.base_cls.Config.name
            else self.base_cls.__name__
        )
        module = self.base_cls.Config.module

        # build selected fields with module/model name
        query = f"with module {module} select {model_name} {{\n"
        for field in self._fields:
            field_name, field_value = field

            if type(field_value) is SelectQueryBuilder:
                query += f"{field_name}: {field_value.build_select_subquery()},"
                query += "\n"
            elif issubclass(type(field_value), Expression):
                expr: Expression = field_value  # type: ignore
                query += f"{field_name}: {expr.to_query()},\n"
            else:
                query += f"{field_name},\n"
        query += "}\n"

        # build filters
        if len(self._filters) > 0:
            query += "filter "
            for idx, filt in enumerate(self._filters):
                query += f"{filt.to_query()}"
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

        query += ";"

        print(query)
        return query

    def build_select_subquery(self) -> str:
        query = "{\n"
        for field in self._fields:
            field_name, field_value = field

            if type(field_value) is SelectQueryBuilder:
                query += field_value.build_select_subquery()
                query += "\n"
            elif issubclass(type(field_value), Expression):
                expr: Expression = field_value  # type: ignore
                query += f"{field_name}: {expr.to_query()},\n"
            else:
                query += f"{field_name},\n"
        query += "}"
        return query
