import typing as t
from dataclasses import dataclass

T = t.TypeVar("T")
V = t.TypeVar("V")


@dataclass(frozen=True)
class EdgeGraphField(t.Generic[T]):
    class_name: str
    name: str
    type: t.Type[T]


class ReflectedFields(t.Generic[T]):
    def __init__(self, cls: t.Type[T]):
        hints = t.get_type_hints(cls)
        del hints["__field_cache__"]

        self.__fields__ = hints
        for field, value in hints.items():
            # set name and value as tuple
            self.__setattr__(
                field, EdgeGraphField(class_name=cls.__name__, name=field, type=value)
            )
