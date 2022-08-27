from pydantic import BaseModel

from edgegraph.reflections import EdgeGraphBase, EdgeGraphMetaclass


class EdgeModel(BaseModel, EdgeGraphBase, metaclass=EdgeGraphMetaclass):
    pass
