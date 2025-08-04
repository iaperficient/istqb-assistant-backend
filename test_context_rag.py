import asyncio 
from app.chat.openai_client import OpenAIClient

async def test_generate_response():
    client = OpenAIClient()

    # Simula un contexto con 2 mensajes previos (user + assistant)
    context = [
        {"role": "user", "content": "What is ISTQB?"},
        {"role": "assistant", "content": "ISTQB is an international software testing certification."}
    ]

    # Mensaje actual
    current_message = "Tell me about the Certified Tester Foundation Level."

    # Llama a generate_response con contexto
    response = await client.generate_response(message=current_message, context=context)

    print("=== RESPONSE ===")
    print(response["response"])

    print("\n=== RAG INFO ===")
    print(response["rag_info"])

# Ejecuta el test
if __name__ == "__main__":
    asyncio.run(test_generate_response())
