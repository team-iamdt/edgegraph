import typing as t

from pydantic import BaseModel

from edgegraph.errors import ConditionValidationError, QueryContextMissmatchError
from edgegraph.expressions.base import Expression
from edgegraph.query_builder.base import (
    AssignType,
    InsertOrUpdateQueryField,
    QueryBuilderBase,
    QueryFieldType,
    T,
)
from edgegraph.query_builder.select import SelectQueryBuilder
from edgegraph.reflections import EdgeGraphField
from edgegraph.types import PrimitiveTypes, QueryResult

V = t.TypeVar("V")


class UpdateQueryBuilder(QueryBuilderBase[T]):
    type = "UPDATE"
    _target_subquery: t.Optional[SelectQueryBuilder]
    _filters: t.Optional[t.List[Expression]]
    _fields: t.List[InsertOrUpdateQueryField]

    def __init__(self, cls: t.Type[T]):
        super().__init__(cls)
        self._target_subquery = None
        self._filters = None
        self._fields = []

    def set_target(
        self,
        subquery: SelectQueryBuilder[T],
    ):
        # check filters are exists
        if self._filters is not None:
            raise ConditionValidationError(
                self.base_type.__name__,
                "Update Target Subquery or Update Filters are can't use both.",
            )

        # Check this subquery is really SelectQueryBuilder
        if not isinstance(subquery, SelectQueryBuilder):
            raise ConditionValidationError(
                self.base_type.__name__, "Subquery is not SelectQueryBuilder"
            )

        # Check Base Type Signature
        if self.base_type.__name__ != subquery.base_type.__name__:
            raise QueryContextMissmatchError(
                self.base_type,
                subquery.base_type,
            )

        self._target_subquery = subquery
        return self

    def add_filter(self, expr: Expression):
        # check filters are exists
        if self._target_subquery is not None:
            raise ConditionValidationError(
                self.base_type.__name__,
                "Update Target Subquery or Update Filters are can't use both.",
            )

        if self._filters is not None and expr in self._filters:
            raise ConditionValidationError(str(expr), "Filter already exists.")

        if self._filters is None:
            self._filters = []

        self._filters.append(expr)
        return self

    def add_field(
        self,
        field: EdgeGraphField[T, V],
        assign: AssignType = AssignType.ASSIGN,
        value: t.Optional[V] = None,
        db_type: t.Optional[PrimitiveTypes] = None,
        expression: t.Optional[Expression] = None,
        subquery: t.Optional[Expression] = None,
    ):
        # check if `value`, `expression`, `subquery` is all none
        if value is None and expression is None and subquery is None:
            raise ConditionValidationError(
                str(field),
                "You must specify one of `value`, `expression`, `subquery`.",
            )

        # check if `value` is available but, value_type is none
        if value is not None and db_type is None:
            raise ConditionValidationError(
                str(field),
                "You must specify `value_type` argument if you specify `value`.",
            )

        # First get field_name, type, context type name
        # And also check field is available for this model
        if isinstance(field, EdgeGraphField):
            field_name = field.name
            field_type = field.type
            upper_type_name = field.base.__name__

            try:
                getattr(self.base_type, field_name)
            except AttributeError:
                raise ConditionValidationError(
                    field_name, f"Field does not exist in {self.base_type}."
                )
        else:
            raise TypeError("field can be EdgeGraphField or str")

        # check field is available in this model
        if upper_type_name != self.base_type.__name__:
            raise QueryContextMissmatchError(upper_type_name, self.base_type)

        # check field already exists.
        if field_name in [field.name for field in self._fields]:
            raise ConditionValidationError(
                field_name, f"Field already exists in {self.base_type}."
            )

        # check field type is correct
        if value is not None and (
            not isinstance(value, field_type) or isinstance(value, BaseModel)
        ):
            raise ConditionValidationError(
                field_name,
                f"Field type is not correct. Expected {field_type}, got {type(value)}",
            )

        if value is not None:
            query_field_type = QueryFieldType.VALUE
            target_expression: t.Optional[Expression] = None
        elif subquery is not None:
            query_field_type = QueryFieldType.SUBQUERY
            target_expression = subquery
        else:
            query_field_type = QueryFieldType.EXPRESSION
            target_expression = expression

        # AssignType.APPEND or AssignType.REMOVE are for Subquery only.
        if query_field_type != QueryFieldType.SUBQUERY and assign != AssignType.ASSIGN:
            assign = AssignType.ASSIGN

        self._fields.append(
            InsertOrUpdateQueryField(
                name=field_name,
                query_field_type=query_field_type,
                value_type=field_type,
                upper_type_name=upper_type_name,
                expression=target_expression,
                edgedb_type=db_type,
                value=value,
                assign_type=assign,
            )
        )

        return self

    def build(self, prefix: str = "") -> QueryResult:
        (module, model_name) = self.base_type.get_schema_config()
        result_args: t.Dict[str, t.Any] = dict()
        self._fields.sort(key=lambda x: x.name)

        query = "update "

        if self._target_subquery is not None:
            target_prefix = f"{prefix}__target" if len(prefix) != 0 else "target"
            target_subquery = self._target_subquery.build(target_prefix)
            result_args.update(target_subquery.kwargs)
            query += f"(\n{target_subquery.query})\n"
        else:
            query += f"{module}::{model_name}\n"

        if self._filters is not None:
            query += "filter "

            for idx, filt in enumerate(self._filters):
                filter_prefix = (
                    f"filter_{id(filt)}"
                    if len(prefix) == 0
                    else f"{prefix}__filter_{id(filt)}"
                )

                filter_result = filt.build(filter_prefix)
                result_args.update(filter_result.kwargs)
                query += f"{filter_result.query}"

                if (idx + 1) != len(self._filters):
                    query += " AND "

                query += "\n"

        query += "set {\n"
        for field in self._fields:
            if field.expression is not None:
                context_prefix = (
                    f"{prefix}__{field.name}" if len(prefix) > 0 else field.name
                )

                expression = field.expression.build(context_prefix)
                result_args.update(expression.kwargs)

                if field.query_field_type == QueryFieldType.EXPRESSION:
                    query += (
                        f"{field.name} {field.assign_type.value} {expression.query},\n"
                    )
                else:
                    # Wrap Subquery
                    query += f"{field.name} {field.assign_type.value} (\n{expression.query}),\n"

            else:
                # already we checked field.value_type before .add_field, but this expression is for type safety.
                assert field.edgedb_type is not None
                key = f"{prefix}__{field.name}" if prefix != "" else field.name
                result_args[key] = field.value
                query += f"{field.name} {field.assign_type.value} <{field.edgedb_type.value}>${key},\n"

        query += "}\n"

        return QueryResult(query, result_args)
