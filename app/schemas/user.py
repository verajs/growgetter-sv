from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from .todo import TodoDisplay
from bson import ObjectId

from typing import Any

from pydantic_core import core_schema

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")

        return ObjectId(value)

class TreeDisplay(BaseModel):
    name: str
    stage: int


class UserBase(BaseModel):
    username: str
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    name: Optional[str] = Field(default=None)
    todos: Optional[List[TodoDisplay]] = Field(default=None)
    trees: Optional[List[TreeDisplay]] = Field(default=None)

        

class UserDisplay(BaseModel):
    id: PyObjectId
    username: str
    email: EmailStr
    name: str
    todos: List[TodoDisplay]
    completed_todos: int
    trees: List[TreeDisplay]

class UserModel(BaseModel):
    id: PyObjectId
    username: str
    email: EmailStr
    hashed_password: str
    name: str
    todos: List[TodoDisplay] = []
    completed_todos: int = 0
    trees: List[TreeDisplay] = Field(default_factory=lambda: [TreeDisplay(name="Uncaria", stage=1)])

    class Config:
        json_encoders = {
            ObjectId: lambda oid: str(oid),
            PyObjectId: lambda oid: str(oid)
        }


class UserAuthenticate(BaseModel):
    username: str
    password: str
