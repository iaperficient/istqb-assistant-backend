from app.rag.vector_store import get_vector_store_manager

def test_rag_query():
    vector_store = get_vector_store_manager()

    if not vector_store.is_initialized():
        print("Vector store no está inicializado o vacío.")
        return

    # Define una consulta que esperas que tenga contexto en tus documentos
    query = "How to enroll an Android device into Microsoft Intune"

    # Obtén el contexto recuperado
    rag_result = vector_store.get_context_for_query(query, certification_code=None)

    print("=== Contexto recuperado ===")
    print(rag_result.get("context", ""))

    print("\n=== Fuentes ===")
    for source in rag_result.get("sources", []):
        print(source)

    print("\n=== Resultado de recuperación ===")
    print("¿Fue exitosa la recuperación?", rag_result.get("retrieval_successful", False))


if __name__ == "__main__":
    test_rag_query()
