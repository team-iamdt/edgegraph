import abc
import typing as t

T = t.TypeVar("T")


class Expression(t.Generic[T], metaclass=abc.ABCMeta):
    base_cls: t.Type[T]

    @abc.abstractmethod
    def to_query(self, prefix: str = "") -> t.Tuple[str, t.Dict[str, t.Any]]:
        pass
