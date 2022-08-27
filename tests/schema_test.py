import typing as t
import uuid

import pendulum
from pydantic import Field

from edgegraph.reflections import EdgeGraphProperty
from edgegraph.schema import EdgeModel


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

        class SchemaConfig:
            module: str = "default"
            name: str = "User"

    # check dot notation
    assert type(UserModel.email) is EdgeGraphProperty

    assert UserModel.__hints__ == {
        "id": uuid.UUID,
        "updated_at": pendulum.DateTime,
        "created_at": pendulum.DateTime,
        "deleted_at": t.Optional[pendulum.DateTime],
        "deleted": bool,
        "email": str,
        "password": str,
        "name": str,
    }
