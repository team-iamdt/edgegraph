import typing as t
from dataclasses import dataclass

from pydantic import BaseModel
from pydantic.typing import resolve_annotations

from edgegraph.errors import CandidateTypeError

ModelMetaclass: t.Type = type(BaseModel)
Base = t.TypeVar("Base")
T = t.TypeVar("T")


@dataclass(frozen=True)
class EdgeGraphField(t.Generic[Base, T]):
    base: t.Type[Base]
    name: str
    type: t.Type[T]


class Configurable:
    __hints__: t.ClassVar[t.Dict[str, t.Type[t.Any]]]

    @classmethod
    def get_schema_config(cls) -> t.Tuple[str, str]:
        model_name = cls.SchemaConfig.name if cls.SchemaConfig.name else cls.__name__
        module = cls.SchemaConfig.module

        return module, model_name

    class SchemaConfig:
        module: str = "default"
        name: str


class EdgeMetaclass(ModelMetaclass):  # type: ignore
    def __new__(
        cls: t.Type["EdgeMetaclass"],
        cls_name: str,
        bases,
        namespace,
        **kwargs,
    ):
        # noinspection PyTypeChecker
        result_type = super().__new__(
            cls, cls_name, bases, namespace=namespace, **kwargs
        )

        hints: t.Dict[str, t.Type[t.Any]] = resolve_annotations(
            namespace.get("__annotations__", {}),
            namespace.get("__module__", None),
        )

        for name, value in hints.items():
            # set name and value as tuple
            # noinspection PyTypeChecker
            field_value = EdgeGraphField(
                name=name,
                type=value,
                base=result_type,
            )

            # set EdgeGraphField in field namespace
            setattr(result_type, name, field_value)

        result_type.__hints__ = hints

        return result_type


def field(candidate: t.Any) -> EdgeGraphField:
    if isinstance(candidate, EdgeGraphField):
        return t.cast(EdgeGraphField, candidate)
    raise CandidateTypeError("Candidate's type must be EdgeGraphField")
