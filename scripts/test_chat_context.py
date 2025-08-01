import requests

def test_chat_context():
    url = "http://localhost:8000/chat/"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1NDAyMjQ5OX0.d9QfXdUV-Bj0NLuj3_Fhz_V7YXRmUaBFltAYNVdlxIo"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": "Hola, esta es una prueba de contexto.",
        "context": None,
        "certification_code": None
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Respuesta del asistente:")
        print(data["response"])
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_chat_context()
