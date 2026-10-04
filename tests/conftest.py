import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine,Session,SQLModel,delete
from database import get_session
from main import app
from models import Task,User
from security import hash_password
TEST_DATABASE_URL=("postgresql+psycopg://postgres:admin@localhost:5432/todo_test")

test_engine=create_engine(TEST_DATABASE_URL,echo=True)


@pytest.fixture
def session():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session

        session.exec(delete(Task))
        session.exec(delete(User))
        session.commit()

@pytest.fixture
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session]=override_get_session

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(session):
    password="testpassword"
    user=User(
        username="testuser",
        password=hash_password(password),
        email="test@example.com",
        role="student"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@pytest.fixture
def test_admin(session):
    password="adminpassword"
    admin=User(
        username="testadmin",
        password=hash_password(password),
        email="admin@example.com",
        role="admin"
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin
