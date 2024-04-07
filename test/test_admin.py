from fastapi import status

from .utils import *
from routers.admin import get_current_user, get_db

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get("api/v1/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Test title',
                                'description': 'Test description',
                                'priority': 5,
                                'completed': False,
                                'owner_id': 1,
                                'id': 1}]


def test_admin_delete_todo(test_todo):
    response = client.delete(f"api/v1/admin/todo/{1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_todo_not_found():
    response = client.delete("api/v1/admin/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
