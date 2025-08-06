import pytest
from dotenv import load_dotenv
import pandas as pd
from fastapi.testclient import TestClient
from main import app
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Cargar variables de entorno desde .env automáticamente
load_dotenv()

client = TestClient(app)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_token():
    import os
    username = os.environ.get("TEST_USER", "testuser")
    password = os.environ.get("TEST_PASS", "testpass")
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password}
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

    import os
    df = pd.read_csv("tests/rag_eval_set.csv")
    similarities = []
    threshold = float(os.environ.get("RAG_TEST_THRESHOLD", "0.75"))
    assert_on_mean = os.environ.get("RAG_TEST_ASSERT_MEAN", "false").lower() == "true"
    min_value = float(os.environ.get("RAG_TEST_MIN", "0.5"))

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
    mean_sim = similarities.mean()
    print(f"Accuracy (sim > {threshold}): {accuracy:.2f}")
    print(f"Mean similarity: {mean_sim:.2f}")

    if assert_on_mean:
        assert mean_sim > min_value, f"Mean similarity {mean_sim:.2f} not greater than {min_value}"
    else:
        assert accuracy > min_value, f"Accuracy {accuracy:.2f} not greater than {min_value}"
