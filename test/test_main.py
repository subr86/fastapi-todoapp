from fastapi.testclient import TestClient
from fastapi import status

import main

client = TestClient(main.app)


def test_main_health():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}

