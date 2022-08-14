import typing as t

from edgegraph.query_builder.select import SelectQueryBuilder
from edgegraph.reflections import ReflectedFields
from pydantic import BaseModel


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
