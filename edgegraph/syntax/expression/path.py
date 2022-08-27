import typing as t
from dataclasses import dataclass, field
from functools import lru_cache

from edgegraph.errors import CandidateTypeError
from edgegraph.reflections import EdgeGraphProperty
from edgegraph.syntax.expression.base import BaseExpression
from edgegraph.types import QueryResult


@dataclass(frozen=True)
class PathExpression(BaseExpression):
    context = "path"
    paths: t.Tuple[EdgeGraphProperty, ...]
    variables: t.Dict[str, t.Any] = field(default_factory=dict)

    @lru_cache
    def to_query(self) -> QueryResult:
        return QueryResult(
            query="".join([f".{p.name}" for p in self.paths]),
            kwargs=self.variables,
        )


def path(*paths: t.Any):
    for idx, p in enumerate(paths):
        if not isinstance(p, EdgeGraphProperty):
            raise CandidateTypeError("Candidate's type must be EdgeGraphField")

        if idx == 0:
            continue

        prev_path = t.cast(EdgeGraphProperty, paths[idx - 1])
        curr_path = t.cast(EdgeGraphProperty, p)

        if not prev_path.linked:
            raise CandidateTypeError(
                f"Previous Property {prev_path} is not linked property.",
            )

        if prev_path.linked_type is not curr_path.type:
            raise CandidateTypeError(
                f"Previous Property {prev_path.linked_type} is not matched with {curr_path.type}.",
            )

    return PathExpression(
        paths=t.cast(t.Tuple[EdgeGraphProperty, ...], paths),
    )
