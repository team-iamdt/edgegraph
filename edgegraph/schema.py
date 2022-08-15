import typing as t

from pydantic import BaseModel

from edgegraph.query_builder.base import SelectQueryField
from edgegraph.query_builder.insert import InsertQueryBuilder
from edgegraph.query_builder.select import SelectQueryBuilder
from edgegraph.reflections import Configurable, EdgeGraphField, EdgeMetaclass


class EdgeModel(BaseModel, Configurable, metaclass=EdgeMetaclass):
    # @classmethod
    # def update(cls) -> UpdateQueryBuilder:
    #     pass
    #
    # @classmethod
    # def delete(cls) -> DeleteQueryBuilder:
    #     pass

    @classmethod
    def select(
        cls,
        fields: t.Optional[t.List[t.Union[EdgeGraphField, SelectQueryField]]] = None,
    ) -> SelectQueryBuilder:
        builder = SelectQueryBuilder(cls)
        if fields is not None:
            fields.sort(key=lambda x: x.name)

            for field in fields:
                builder = builder.field(field)

        return builder

    @classmethod
    def insert(cls) -> InsertQueryBuilder:
        return InsertQueryBuilder(cls)
