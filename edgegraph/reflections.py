import typing as t
from dataclasses import dataclass

from pydantic import BaseModel

ModelMetaclass: t.Type = type(BaseModel)


T = t.TypeVar("T")
V = t.TypeVar("V")


@dataclass(frozen=True)
class EdgeGraphField(t.Generic[T]):
    class_name: str
    name: str
    type: t.Type[T]


class EdgeMetaclass(ModelMetaclass):  # type: ignore
    def __new__(cls: t.Type["EdgeMetaclass"], cls_name: str, bases, attrs):
        # noinspection PyTypeChecker
        result_type = super().__new__(cls, cls_name, bases, attrs)

        hints = t.get_type_hints(result_type)

        # Remove ClassVar
        names = []
        for name, typ in hints.items():
            if t.get_origin(typ) is t.ClassVar:
                names.append(name)
        for name in names:
            del hints[name]

        result_type.__hints__ = hints
        for field, value in hints.items():
            # set name and value as tuple
            field_value = EdgeGraphField(class_name=cls_name, name=field, type=value)
            setattr(result_type, field, field_value)

        return result_type
