import typing as t
import uuid

import pendulum
from pydantic import Field

from edgegraph.schema import EdgeModel


class UserModel(EdgeModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid1)
    updated_at: pendulum.DateTime = Field(default_factory=pendulum.now)
    created_at: pendulum.DateTime = Field(default_factory=pendulum.now)
    deleted_at: t.Optional[pendulum.DateTime] = Field(default=None)
    deleted: bool = Field(default=False)

    email: str
    password: str
    name: str = Field(min_length=3)

    class SchemaConfig:
        module: str = "default"
        name: str = "User"


class MemoModel(EdgeModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid1)
    updated_at: pendulum.DateTime = Field(default_factory=pendulum.now)
    created_at: pendulum.DateTime = Field(default_factory=pendulum.now)
    deleted_at: t.Optional[pendulum.DateTime] = Field(default=None)
    deleted: bool = Field(default=False)

    title: str
    content: str
    tags: t.List[str] = Field(default=[])

    created_by: UserModel
    accessable_users: t.List[UserModel] = Field(default=[])

    class SchemaConfig:
        module: str = "default"
        name: str = "Memo"


class CommentModel(EdgeModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid1)
    updated_at: pendulum.DateTime = Field(default_factory=pendulum.now)
    created_at: pendulum.DateTime = Field(default_factory=pendulum.now)
    deleted_at: t.Optional[pendulum.DateTime] = Field(default=None)
    deleted: bool = Field(default=False)

    created_by: UserModel
    memo: MemoModel
    content: str

    class SchemaConfig:
        module: str = "default"
        name: str = "Comment"
