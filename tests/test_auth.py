import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_invalid_user():
    response = client.post(
        "/auth/login",
        data={"username": "usuario_invalido", "password": "incorrecta"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_register_and_login():
    # Registro
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass",
        "role": "user"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code in (200, 400)  # Puede fallar si ya existe

    # Login
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "testuser"
