import typing as t

from edgegraph.query_builder.select import SelectQueryBuilder
from pydantic import BaseModel

T = t.TypeVar("T")
V = t.TypeVar("V")


class ReflectedFields(t.Generic[T]):
    def __init__(self, cls: t.Type[T]):
        hints = t.get_type_hints(cls)
        del hints["__field_cache__"]

        self.__fields__ = hints
        for field, value in hints.items():
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

    # @classmethod
    # def insert(cls) -> InsertQueryBuilder:
    #     pass
    #
    # @classmethod
    # def update(cls) -> UpdateQueryBuilder:
    #     pass
    #
    # @classmethod
    # def delete(cls) -> DeleteQueryBuilder:
    #     pass

    @classmethod
    def select(cls) -> SelectQueryBuilder:
        return SelectQueryBuilder(cls)

    class Config:
        module: str = "default"
        name: str
