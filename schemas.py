from pydantic import BaseModel
from typing import Literal


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str



class UserUpdate(BaseModel):
    username:str|None=None
    email: str | None = None
    role: str | None = None



class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

class UserUpdateFull(BaseModel):
    username: str
    email: str
    role: str

class Taskcreate(BaseModel):
    title:str
    assign_to_User:str

class Taskresponse(BaseModel):
    id: int
    title: str
    assigned_to: str
    status: str

class TaskReview(BaseModel):
    status:Literal["completed","rejected"]

class TaskListResponse(BaseModel):
    message: str
    tasks: list[Taskresponse]


