from fastapi import status
from sqlalchemy.testing.pickleable import User

from .utils import *
from routers.user import get_current_user, get_db

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_returned_user(test_user):
    response = client.get('api/v1/user/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'subr'
    assert response.json()['email'] == 'subr86@gmail.com'
    assert response.json()['first_name'] == 'Serhii'
    assert response.json()['last_name'] == 'Petryk'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '+380977652728'


def test_change_password_success(test_user):
    response = client.put('api/v1/user/password', json={'password': '3360664', 'new_password': '33606641'})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    response = client.put('api/v1/user/password', json={'password': '33606641', 'new_password': '33606642'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Current password is incorrect.'}


def test_change_phone_success(test_user):
    response = client.put('api/v1/user/phone', params={'phone_number': '+380977652729'})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.id == 1).first()
    assert user.phone_number == '+380977652729'
