import chromadb

PERSIST_DIRECTORY = "./app/chroma_db"
COLLECTION_NAME = "ct-genai"

client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = client.get_or_create_collection(COLLECTION_NAME)

try:
    # Esto funciona solo en versiones recientes de Chroma
    count = collection.count()
    print(f"✅ La colección '{COLLECTION_NAME}' contiene {count} documentos.")
except Exception as e:
    print("⚠️ No se pudo obtener la cantidad de documentos:", e)

# Intentar recuperar los primeros documentos si hay alguno
try:
    results = collection.get(ids=None)  # Si esto da error, prueba sin argumentos: collection.get()
    print(f"🔎 Se recuperaron {len(results['ids'])} documentos.")
    for i, doc in enumerate(results["documents"][:3]):
        print(f"\n📝 Documento {i+1}:\n{doc}\n{'-'*40}")
except Exception as e:
    print("⚠️ No se pudo recuperar documentos:", e)
