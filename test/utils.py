from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest

from main import app
from database import Base
from models import Todos, Users
from routers.auth import bcrypt_context

# Sqlite3
SQLALCHEMY_DATABASE_URI = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {
        'id': 1,
        'username': 'test',
        'user_role': 'admin'
    }


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title='Test title',
        description='Test description',
        priority=5,
        completed=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos;"))
        conn.commit()


@pytest.fixture
def test_user():
    user = Users(
        email='subr86@gmail.com',
        username='subr',
        first_name='Serhii',
        last_name='Petryk',
        password=bcrypt_context.hash('3360664'),
        role='admin',
        phone_number='+380977652728'
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users;"))
        conn.commit()
