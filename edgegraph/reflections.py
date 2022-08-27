import typing as t
from dataclasses import dataclass

from pydantic import BaseModel
from pydantic.typing import resolve_annotations

from edgegraph.errors import CandidateTypeError

ModelMetaclass: t.Type = type(BaseModel)
Base = t.TypeVar("Base")
T = t.TypeVar("T")


@dataclass(frozen=True)
class EdgeGraphProperty(t.Generic[Base, T]):
    defined_at: t.Type[Base]
    context: t.Type[Base]
    inherited: bool
    name: str
    type: t.Type[T]
    linked: bool
    linked_type: t.Optional[t.Type[T]] = None


class EdgeGraphBase:
    __hints__: t.ClassVar[t.Dict[str, t.Type[t.Any]]]
    __properties__: t.ClassVar[t.Dict[str, EdgeGraphProperty]]

    @classmethod
    def get_type_name(cls) -> str:
        type_name = getattr(cls.TypeConfig, "name", cls.__name__)
        module = getattr(cls.TypeConfig, "module", "default")
        return f"{module}::{type_name}"

    @classmethod
    def is_abstract_type(cls) -> bool:
        return getattr(cls.TypeConfig, "abstract_type", False)

    @classmethod
    def get_type_config(cls) -> t.Tuple[str, str, bool]:
        module = str(getattr(cls.TypeConfig, "module", "default"))
        type_name = str(getattr(cls.TypeConfig, "name", cls.__name__))
        is_abstract_type = getattr(cls.TypeConfig, "abstract_type", False)
        return module, type_name, is_abstract_type

    @classmethod
    def _get_property(cls, name: str) -> t.Optional[EdgeGraphProperty]:
        return cls.__properties__.get(name, None)

    @classmethod
    def _get_properties(cls) -> t.Dict[str, EdgeGraphProperty]:
        return cls.__properties__

    @classmethod
    def property(cls, name: str):
        return cls._get_property(name)

    @classmethod
    def prop(cls, name):
        return cls._get_property(name)

    @classmethod
    def properties(cls):
        return cls._get_properties()

    @classmethod
    def props(cls):
        return cls._get_properties()

    class TypeConfig:
        module: str = "default"
        name: t.Optional[str] = None
        abstract_type: bool = False


class EdgeGraphMetaclass(ModelMetaclass):  # type: ignore
    def __new__(
        cls: t.Type["EdgeGraphMetaclass"],
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

        properties: t.Dict[str, EdgeGraphProperty] = dict()
        for name, value in hints.items():
            # set name and value as tuple
            linked = False
            linked_type = None

            # 1. value 그 자체가 BaseEdgeDBModel인지 체크한다.
            if EdgeGraphBase in getattr(value, "__bases__", []):
                linked_type = value
                linked = True

            # 2. Optional / Union일 경우
            available_types = list(t.get_args(value))
            if len(available_types) != 0:
                for available_type in available_types:
                    if EdgeGraphBase in getattr(available_type, "__bases__", []):
                        linked_type = available_type
                        linked = True

            # noinspection PyTypeChecker
            field_value = EdgeGraphProperty(
                defined_at=result_type,
                context=result_type,
                inherited=False,
                name=name,
                type=value,
                linked=linked,
                linked_type=linked_type,
            )

            # set EdgeGraphField in field namespace
            setattr(result_type, name, field_value)

        if getattr(result_type, "__properties__", None) is not None:
            upper_type_fields = t.cast(
                t.Dict[str, EdgeGraphProperty], result_type.__properties__
            )
            for k, v in upper_type_fields.items():
                properties[k] = EdgeGraphProperty(
                    defined_at=v.defined_at,
                    context=result_type,
                    inherited=True,
                    name=v.name,
                    type=v.type,
                    linked=v.linked,
                )

        result_type.__hints__ = hints
        result_type.__properties__ = properties

        return result_type


def field(candidate: t.Any) -> EdgeGraphProperty:
    if isinstance(candidate, EdgeGraphProperty):
        return t.cast(EdgeGraphProperty, candidate)
    raise CandidateTypeError("Candidate's type must be EdgeGraphField")
