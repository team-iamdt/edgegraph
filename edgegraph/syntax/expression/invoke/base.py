import typing as t
from dataclasses import dataclass, field

from edgegraph.syntax.base import BaseSyntax
from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult

# TODO(Hazealign): How can we represent every Primitive Types in EdgeQL?
ValuedArgument: t.TypeAlias = t.Tuple[str, t.Any]
Argument: t.TypeAlias = t.Union[BaseSyntax, ValuedArgument]


@dataclass(frozen=True)
class InvokeExpression(BaseExpression):
    context = "invoke"
    function_name: str
    arguments: t.Tuple[Argument, ...]
    module_name: t.Optional[str] = None
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    def to_query(self) -> QueryResult:
        resolved_module_name = "" if self.module_name is None else self.module_name
        resolved_function = f"{resolved_module_name}::{self.function_name}"

        kwargs: t.Dict[str, t.Any] = self.variables.copy()
        query = f"{resolved_function}("

        for idx, arg in enumerate(self.arguments):
            if isinstance(arg, BaseSyntax):
                result = arg.to_query()
                query += result.query
                kwargs.update(result.kwargs)

            else:
                (edgedb_type, value) = arg
                variable_name = f"{self.context}_{id(self)}_{idx}"
                query += f"<{edgedb_type}>${variable_name}"
                kwargs.update(
                    {
                        variable_name: value,
                    }
                )

            if (idx - 1) != len(self.arguments):
                query += ", "

        query += ")"
        return QueryResult(
            query=query,
            kwargs=kwargs,
        )
