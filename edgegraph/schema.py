import typing as t

from pydantic import BaseModel

from edgegraph.query_builder.select import SelectQueryBuilder
from edgegraph.reflections import ReflectedFields


ModelMetaclass: t.Type = type(BaseModel)


class EdgeMetaclass(ModelMetaclass):  # type: ignore
    def __new__(cls: t.Type, cls_name: str, bases, attrs):
        # noinspection PyTypeChecker
        result_type = super().__new__(cls, cls_name, bases, attrs)
        result_type.fields = ReflectedFields(result_type)
        return result_type


class EdgeModel(BaseModel, metaclass=EdgeMetaclass):
    fields: t.ClassVar[ReflectedFields]

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
