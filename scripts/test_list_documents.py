import requests

current_user: User = Depends(get_current_active_user)
url = "http://localhost:8000/users/me"  # ← Ajusta esto a un endpoint que devuelva el usuario autenticado
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbjQzIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzU0MzYzMjI1fQ.NutSQkFNpbTFha26tnBJA0ElDljGJZGQRP5m_pk6b38"
}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.json())