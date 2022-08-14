import typing as t
import uuid

from edgegraph.reflections import EdgeGraphField
from edgegraph.schema import EdgeModel, ReflectedFields
import pendulum
from pydantic import Field


def test_reflect_fields_are_valid():
    class UserModel(EdgeModel):
        id: uuid.UUID = Field(default=uuid.uuid1())
        updated_at: pendulum.DateTime = Field(default=pendulum.now())
        created_at: pendulum.DateTime = Field(None)
        deleted_at: t.Optional[pendulum.DateTime] = Field(default=None)
        deleted: bool = Field(default=False)

        email: str
        password: str
        name: str = Field(min_length=3)

        class Config:
            module: str = "default"
            name: str = "User"

    assert type(UserModel.fields()) is ReflectedFields

    # check dot notation
    assert UserModel.fields().email == EdgeGraphField("UserModel", "email", str)
    assert UserModel.fields().created_at == EdgeGraphField(
        "UserModel", "created_at", pendulum.DateTime
    )

    assert UserModel.fields().__fields__ == {
        "id": uuid.UUID,
        "updated_at": pendulum.DateTime,
        "created_at": pendulum.DateTime,
        "deleted_at": t.Optional[pendulum.DateTime],
        "deleted": bool,
        "email": str,
        "password": str,
        "name": str,
    }
