import os

from sqlmodel import SQLModel,create_engine,Session
from dotenv import load_dotenv
load_dotenv()
engine_url=os.getenv("engine_url")
if not engine_url:
    raise ValueError("engine_url is not configured")

engine=create_engine(engine_url,echo=True)


def create_db_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
