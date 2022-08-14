import typing as t

from pydantic import BaseModel


T = t.TypeVar("T", bound=BaseModel)
V = t.TypeVar("V")


class ReflectedFields(t.Generic[T]):
    def __init__(self, cls: t.Type[T]):
        self.__fields__ = t.get_type_hints(cls)
        for field, value in self.__fields__.items():
            # set name and value as tuple
            self.__setattr__(field, (field, value))


class EdgeModel(BaseModel):
    __field_cache__: t.Optional[ReflectedFields] = None

    @classmethod
    def fields(cls):
        # use cache if available
        if cls.__field_cache__ is not None:
            return cls.__field_cache__

        cls.__field_cache__ = ReflectedFields(cls)
        return cls.__field_cache__

    class Config:
        module: str = "default"
        name: str
