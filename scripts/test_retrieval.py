from app.rag.vector_store import get_vector_store_manager

rag = get_vector_store_manager()
result = rag.get_context_for_query("¿Qué técnicas se pueden usar para refinar prompts de GenAI?")

if result["retrieval_successful"]:
    print("✅ Contexto encontrado:")
    print(result["context"])
else:
    print("⚠️ No se encontraron documentos relacionados.")
