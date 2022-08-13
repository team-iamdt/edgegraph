from pydantic import BaseModel


class EdgeModel(BaseModel):
    class Config:
        module: str = "default"
        name: str
