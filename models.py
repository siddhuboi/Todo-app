from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id:int|None= Field(default=None, primary_key=True)

    username: str
    email: str
    password: str
    role: str


class Task(SQLModel, table=True):
    id:int|None = Field(default=None, primary_key=True)

    title: str

    assigned_to: int = Field(
        foreign_key="user.id"
    )
    assigned_by: int = Field(
        foreign_key="user.id"
    )

    status: str = "pending"