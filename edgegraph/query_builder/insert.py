import typing as t

from pydantic import BaseModel

from edgegraph.errors import ConditionValidationError, QueryContextMissmatchError
from edgegraph.expressions.base import Expression
from edgegraph.query_builder.base import (
    InsertQueryField,
    QueryBuilderBase,
    QueryFieldType,
    T,
)
from edgegraph.reflections import EdgeGraphField
from edgegraph.types import PrimitiveTypes, QueryResult

V = t.TypeVar("V")


class InsertQueryBuilder(QueryBuilderBase[T]):
    type = "INSERT"

    _unless_conflict: t.Optional[t.List[str]]
    _unless_conflict_else: t.Optional[QueryBuilderBase[T]]
    _fields: t.List[InsertQueryField]

    def __init__(self, cls: t.Type[T]):
        super().__init__(cls)
        self._unless_conflict = None
        self._unless_conflict_else = None
        self._fields = []

    def add_field(
        self,
        field: t.Union[EdgeGraphField[T, V], str],
        value: t.Optional[V] = None,
        db_type: t.Optional[PrimitiveTypes] = None,
        expression: t.Optional[Expression] = None,
        subquery: t.Optional[Expression] = None,
    ):
        # check if `value`, `expression`, `subquery` is all none
        if value is None and expression is None and subquery is None:
            raise ConditionValidationError(
                str(field), "You must specify one of `value`, `expression`, `subquery`."
            )

        # check if `value` is available but, value_type is none
        if value is not None and db_type is None:
            raise ConditionValidationError(
                str(field),
                "You must specify `value_type` argument if you specify `value`.",
            )

        # First get field_name, type, context type name
        # And also check field is available for this model
        if isinstance(field, str):
            field_name = field
            try:
                field_info: EdgeGraphField = getattr(self.base_type, "field_name")
                field_type = field_info.type
                upper_type_name = field_info.base.__name__
            except AttributeError:
                raise ConditionValidationError(
                    field_name, f"Field does not exist in {self.base_type}."
                )
        elif isinstance(field, EdgeGraphField):
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

        self._fields.append(
            InsertQueryField(
                name=field_name,
                query_field_type=query_field_type,
                value_type=field_type,
                upper_type_name=upper_type_name,
                expression=target_expression,
                edgedb_type=db_type,
                value=value,
            )
        )

        return self

    def unless_conflict(
        self,
        *fields: t.Union[str, EdgeGraphField],
        else_query: QueryBuilderBase[T] = None,
    ):
        # TODO(Hazealign): Check deep link fields when we support it.
        new_fields = []

        for field in fields:
            if isinstance(field, str):
                new_fields.append(field[1:] if field.startswith(".") else field)
            elif isinstance(field, EdgeGraphField):
                new_fields.append(field.name)
            else:
                raise TypeError("Fields can be str or EdgeGraphField.")

        if self._unless_conflict is None:
            self._unless_conflict = new_fields
        else:
            self._unless_conflict.extend(new_fields)

        if else_query is not None:
            self._unless_conflict_else = else_query

        return self

    def build(self, prefix: str = "") -> QueryResult:
        # TODO(Hazealign): Check required fields are all settled.
        (module, model_name) = self.base_type.get_schema_config()
        result_args: t.Dict[str, t.Any] = dict()
        self._fields.sort(key=lambda x: x.name)

        # build fields with module/model name
        query = f"insert {module}::{model_name} {{\n"
        for field in self._fields:
            context_prefix = (
                f"{prefix}__{field.name}" if len(prefix) > 0 else field.name
            )

            if field.expression is not None:
                expression = field.expression.build(context_prefix)
                result_args.update(expression.kwargs)

                if field.query_field_type == QueryFieldType.EXPRESSION:
                    query += f"{field.name}: {expression.query},\n"
                else:
                    # Wrap Subquery
                    query += f"{field.name}: (\n{expression.query}),\n"

            else:
                # already we checked field.value_type before .add_field, but this expression is for type safety.
                assert field.edgedb_type is not None
                key = f"{prefix}__{field.name}" if prefix != "" else field.name
                result_args[key] = field.value
                query += f"{field.name}: <{field.edgedb_type.value}>${key},\n"

        query += "}\n"

        # build unless conflict
        if self._unless_conflict is not None:
            self._unless_conflict.sort()

            unless_conflicts = ", ".join(map(lambda x: f".{x}", self._unless_conflict))
            query += f"unless conflict on ({unless_conflicts})\n"

            if self._unless_conflict_else is not None:
                unless_conflict_prefix = (
                    f"{prefix}__unless_conflict"
                    if len(prefix) > 0
                    else "unless_conflict"
                )
                conflict_else = self._unless_conflict_else.build(unless_conflict_prefix)
                result_args.update(conflict_else.kwargs)

                query += f"else (\n{conflict_else.query})"

        return QueryResult(query=query, kwargs=result_args)
