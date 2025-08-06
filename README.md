# ISTQB Assistant Backend

This project is an AI-powered assistant for ISTQB software testing concepts, built with FastAPI. It includes authentication, chat endpoints, RAG (Retrieval-Augmented Generation) evaluation, and automated tests.

## Project Structure

```
istqb-assistant-backend/
│
├── app/
│   ├── auth/                # Authentication logic and routes
│   ├── chat/                # Chat endpoints and RAG logic
│   ├── certification/       # Certification endpoints
│   ├── database/            # Database connection and models
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── utils/               # Utility functions (security, etc.)
│
├── scripts/                 # Manual test scripts
│
├── tests/                   # Automated tests (pytest)
│   ├── test_auth.py         # Auth endpoint tests
│   ├── test_chat.py         # Chat endpoint tests
│   ├── test_rag_semantic.py # RAG semantic evaluation tests
│   ├── rag_eval_set.csv     # Questions and expected answers for RAG evaluation
│
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   - Create a `.env` file with your secrets (e.g. `OPENAI_API_KEY`, `SECRET_KEY`, etc.)

3. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

## Testing

- **Run all tests**
  ```bash
  pytest
  ```

- **RAG semantic evaluation**
  - The test `tests/test_rag_semantic.py` reads `tests/rag_eval_set.csv`, sends each question to `/chat/`, and compares the response to the expected answer using semantic similarity (sentence-transformers).
  - Metrics printed: accuracy, mean similarity.

## Endpoints

- `/auth/login` - User authentication
- `/chat/` - Chat with the assistant (POST)
- `/chat/conversations` - List user conversations (GET)
- `/chat/history` - Delete chat history (DELETE)
- Other endpoints for certification and user management

## Contributing

Feel free to open issues or submit pull requests for improvements or bug fixes.

## License

MIT License