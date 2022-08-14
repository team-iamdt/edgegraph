import typing as t

T = t.TypeVar("T")


class Expression(t.Generic[T]):
    base_cls: t.Type[T]

    def to_query(self) -> str:
        pass
