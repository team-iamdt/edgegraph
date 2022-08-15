import typing as t

from pydantic import BaseModel

from edgegraph.query_builder.select import SelectQueryBuilder
from edgegraph.reflections import EdgeMetaclass


class EdgeModel(BaseModel, metaclass=EdgeMetaclass):
    __hints__: t.ClassVar[t.Dict[str, t.Type[t.Any]]]

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
