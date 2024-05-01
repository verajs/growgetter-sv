from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, Set
from bson import ObjectId

from typing import List
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




class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    days_active: Set[str] = Field(default_factory=set)

    # This might not be necessary unless days_active is supposed to handle dates
    @validator('days_active', pre=True, each_item=True)
    def validate_days_active(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return datetime(v.year, v.month, v.day)
        return v

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    days_active: List[str] = Field(default_factory=list)
    completed: Optional[bool] = False
    completed_date: Optional[datetime] = None

    
class TodoUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    days_active: Optional[List[str]]
    completed: Optional[bool] = False  # Default to False if not provided
    completed_date: Optional[datetime] = None  # Default to None if not provided


class TodoDisplay(BaseModel):
    id: PyObjectId
    title: str
    description: Optional[str]
    days_active: List[str]
    created_date: Optional[datetime] = None
    completed: Optional[bool] = False
    completed_date: Optional[datetime] = None



class TodoBase(BaseModel):
    id: PyObjectId
    title: str
    description: Optional[str] = None
    created_date: date = Field(default_factory=date.today)
    completed: bool = False
    completed_date: Optional[date] = None  # Date when the todo was last completed
    days_active: List[str] = Field(default_factory=list)
