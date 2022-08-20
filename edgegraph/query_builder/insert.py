import typing as t

from edgedb.abstract import QueryWithArgs
from pydantic import BaseModel

from edgegraph.errors import ConditionValidationError, QueryContextMissmatchError
from edgegraph.expressions.base import Expression
from edgegraph.query_builder.base import InsertQueryField, QueryBuilderBase, T
from edgegraph.reflections import EdgeGraphField
from edgegraph.types import PrimitiveTypes

V = t.TypeVar("V")


class InsertQueryBuilder(QueryBuilderBase[T]):
    query_type = "INSERT"

    _unless_conflict: t.Optional[t.List[str]]
    _unless_conflict_else: t.Optional[QueryBuilderBase]
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
        value_type: t.Optional[PrimitiveTypes] = None,
        expression: t.Optional[Expression] = None,
        subquery: t.Optional[QueryBuilderBase] = None,
    ):
        # check if `value`, `expression`, `subquery` is all none
        if value is None and expression is None and subquery is None:
            raise ConditionValidationError(
                str(field), "You must specify one of `value`, `expression`, `subquery`."
            )

        # check if `value` is available but, value_type is none
        if value is not None and value_type is None:
            raise ConditionValidationError(
                str(field),
                "You must specify `value_type` argument if you specify `value`.",
            )

        # First get field_name, type, context type name
        # And also check field is available for this model
        if isinstance(field, str):
            field_name = field
            try:
                field_info: EdgeGraphField = getattr(self.base_cls, "field_name")
                field_type = field_info.type
                upper_type_name = field_info.base.__name__
            except AttributeError:
                raise ConditionValidationError(
                    field_name, f"Field does not exist in {self.base_cls}."
                )
        elif isinstance(field, EdgeGraphField):
            field_name = field.name
            field_type = field.type
            upper_type_name = field.base.__name__

            try:
                getattr(self.base_cls, field_name)
            except AttributeError:
                raise ConditionValidationError(
                    field_name, f"Field does not exist in {self.base_cls}."
                )
        else:
            raise TypeError("field can be EdgeGraphField or str")

        # check field is available in this model
        if upper_type_name != self.base_cls.__name__:
            raise QueryContextMissmatchError(upper_type_name, self.base_cls)

        # check field already exists.
        if field_name in [field.name for field in self._fields]:
            raise ConditionValidationError(
                field_name, f"Field already exists in {self.base_cls}."
            )

        # check field type is correct
        if value is not None and (
            not isinstance(value, field_type) or isinstance(value, BaseModel)
        ):
            raise ConditionValidationError(
                field_name,
                f"Field type is not correct. Expected {field_type}, got {type(value)}",
            )

        self._fields.append(
            InsertQueryField(
                name=field_name,
                type=field_type,
                upper_type_name=upper_type_name,
                expression=expression,
                subquery=subquery,
                value_type=value_type,
                value=value,
            )
        )

        return self

    def unless_conflict(
        self,
        *fields: t.Union[str, EdgeGraphField],
        else_query: QueryBuilderBase = None,
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

    def build(self, prefix: str = "") -> QueryWithArgs:
        # TODO(Hazealign): Check required fields are all settled.
        (module, model_name) = self.base_cls.get_schema_config()
        result_args: t.Dict[str, t.Any] = dict()
        self._fields.sort(key=lambda x: x.name)

        # build fields with module/model name
        query = f"insert {module}::{model_name} {{\n"
        for field in self._fields:
            context_prefix = (
                f"{prefix}__{field.name}" if len(prefix) > 0 else field.name
            )

            if field.expression is not None:
                expr_query, expr_dict = field.expression.to_query(context_prefix)
                result_args.update(expr_dict)
                query += f"{field.name}: {expr_query},\n"

            elif field.subquery is not None:
                subquery = field.subquery.build(context_prefix)
                result_args.update(subquery.kwargs)
                query += f"{field.name}: (\n{subquery.query}),\n"

            else:
                assert field.value_type is not None
                key = f"{prefix}__{field.name}" if prefix != "" else field.name
                result_args[key] = field.value
                query += f"{field.name}: <{field.value_type.value}>${key},\n"

        query += "}\n"

        # build unless conflict
        if self._unless_conflict is not None:
            self._unless_conflict.sort()

            unless_conflicts = ", ".join(map(lambda x: f".{x}", self._unless_conflict))
            query += f"unless conflict on ({unless_conflicts})\n"

            if self._unless_conflict_else is not None:
                conflict_else_subquery = self._unless_conflict_else.build_string()
                query += f"else (\n{conflict_else_subquery})"

        return QueryWithArgs(
            query=query,
            args=(),
            kwargs=result_args,
        )

    def build_string(self, prefix: str = "") -> str:
        query_result = self.build(prefix)
        query = query_result.query

        for key, value in query_result.kwargs.items():
            query = query.replace(f"${key}", f"'{str(value)}'")

        return query
