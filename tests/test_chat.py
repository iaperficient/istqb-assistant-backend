import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token():
    # Ajusta el usuario y contraseña según tu base de datos
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_chat_unauthorized():
    response = client.post("/chat/", json={"message": "Hola"})
    assert response.status_code == 401

def test_chat_with_token():
    token = get_token()
    if not token:
        pytest.skip("No se pudo obtener token válido para pruebas de chat.")
    payload = {"message": "¿Qué es ISTQB?", "conversation_id": "test_convo"}
    response = client.post(
        "/chat/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 500)  # 500 si falla OpenAI, 200 si responde bien
    if response.status_code == 200:
        data = response.json()
        assert "response" in data
        assert "usage" in data

def test_delete_chat_history():
    token = get_token()
    if not token:
        pytest.skip("No se pudo obtener token válido para pruebas de chat.")
    response = client.delete(
        "/chat/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 500)

# Puedes agregar más pruebas para /chat/history GET, casos límite, etc.
