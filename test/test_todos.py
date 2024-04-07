from fastapi import status

from routers.auth import get_current_user
from routers.todos import get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("api/v1/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Test title',
                                'description': 'Test description',
                                'priority': 5,
                                'completed': False,
                                'owner_id': 1,
                                'id': 1}]


def test_read_one_authenticated(test_todo):
    response = client.get("api/v1/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'Test title',
                               'description': 'Test description',
                               'priority': 5,
                               'completed': False,
                               'owner_id': 1,
                               'id': 1}


def test_read_one_authenticated_not_found():
    response = client.get("api/v1/todos/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


def test_create_todo(test_todo):
    request_data = {
        'title': 'Test title new',
        'description': 'Test description',
        'priority': 3,
        'completed': False
    }
    response = client.post("api/v1/todos/todo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')


def test_update_todo(test_todo):
    request_data = {
        'title': 'Test title new',
        'description': 'Test description',
        'priority': 3,
        'completed': False
    }
    response = client.put("api/v1/todos/todo/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get('title')


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Test title new',
        'description': 'Test description',
        'priority': 3,
        'completed': False
    }
    response = client.put("api/v1/todos/todo/2", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


def test_delete_todo(test_todo):
    response = client.delete("api/v1/todos/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete("api/v1/todos/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
