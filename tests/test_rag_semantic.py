import pytest
import pandas as pd
from fastapi.testclient import TestClient
from main import app
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

client = TestClient(app)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_token():
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def semantic_similarity(a, b):
    emb_a = model.encode([a])[0]
    emb_b = model.encode([b])[0]
    return cosine_similarity([emb_a], [emb_b])[0][0]

def test_rag_semantic_eval():
    token = get_token()
    if not token:
        pytest.skip("No se pudo obtener token válido para pruebas de RAG.")

    df = pd.read_csv("tests/rag_eval_set.csv")
    similarities = []
    threshold = 0.75

    for _, row in df.iterrows():
        payload = {"message": row["Pregunta"], "conversation_id": "eval"}
        response = client.post(
            "/chat/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        answer = response.json()["response"]
        sim = semantic_similarity(answer, row["Respuesta esperada"])
        similarities.append(sim)

    similarities = np.array(similarities)
    accuracy = np.mean(similarities > threshold)
    print(f"Accuracy (sim > {threshold}): {accuracy:.2f}")
    print(f"Mean similarity: {similarities.mean():.2f}")

    assert accuracy > 0.5  # Ajusta según tu criterio
