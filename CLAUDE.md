# ISTQB Assistant Backend

## Project Overview
An AI-powered backend API for ISTQB (International Software Testing Qualifications Board) software testing concepts. Built with FastAPI and integrates with OpenAI for intelligent responses about software testing methodologies and best practices.

## Architecture

### Tech Stack
- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with OAuth2
- **AI Integration**: OpenAI GPT-3.5-turbo
- **Password Security**: bcrypt hashing

### Project Structure
```
app/
├── auth/           # Authentication & authorization
├── chat/           # Chat functionality with OpenAI
├── database/       # Database connection & session management
├── models/         # SQLAlchemy database models
├── schemas/        # Pydantic data models
└── utils/          # Security utilities
```

## Key Components

### Database (`app/database/`)
- **Connection**: `connection.py` - SQLite database setup with session management
- **Database File**: `istqb_assistant.db` (SQLite)
- **Session Management**: Dependency injection pattern for database sessions

### Models (`app/models/`)
- **User Model**: `user.py` - User table with authentication fields
  - Fields: id, username, email, hashed_password, is_active, created_at, updated_at

### Authentication System (`app/auth/`)
- **OAuth2**: `oauth2.py` - JWT token validation and user authentication
- **Routes**: `routes.py` - Registration and login endpoints
- **Security**: JWT-based authentication with 30-minute token expiration

### Chat System (`app/chat/`)
- **OpenAI Client**: `openai_client.py` - OpenAI integration for ISTQB assistance
- **Routes**: `chat.py` - Protected chat endpoints requiring authentication
- **Model**: Uses GPT-3.5-turbo with ISTQB-specific system prompt

### Schemas (`app/schemas/`)
- **User Schemas**: Registration, response, and token models
- **Chat Schemas**: Message input and response models with usage tracking

### Security (`app/utils/`)
- **Password Hashing**: bcrypt for secure password storage
- **JWT Management**: Token creation and verification
- **Secret Key**: Hardcoded (needs environment variable in production)

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)

### Chat
- `POST /chat/` - Send message to ISTQB assistant (requires authentication)

### Health
- `GET /health` - Service health check

## Dependencies

### Core Dependencies
```
fastapi[standard]      # Web framework
uvicorn[standard]      # ASGI server
sqlalchemy            # ORM
python-jose[cryptography]  # JWT handling
passlib[bcrypt]       # Password hashing
python-multipart      # Form data handling
pydantic-settings     # Settings management
python-dotenv         # Environment variables
openai               # OpenAI API client
```

## Environment Variables
- `OPENAI_API_KEY` - Required for OpenAI integration
- Database URL is hardcoded to SQLite (consider making configurable)

## Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload
```

## Development Commands
- **Start Server**: `uvicorn main:app --reload`
- **Database**: Auto-creates tables on startup via `User.metadata.create_all(bind=engine)`

## Security Considerations
1. **Secret Key**: Currently hardcoded in `app/utils/security.py:7` - should use environment variable
2. **CORS**: Currently allows all origins (`allow_origins=["*"]`)
3. **Database**: SQLite with check_same_thread disabled for FastAPI compatibility
4. **Password Security**: Uses bcrypt hashing (secure)

## Key Files to Understand
- `main.py:13-32` - FastAPI app configuration and middleware setup
- `app/auth/routes.py:12-53` - User registration and login logic
- `app/chat/openai_client.py:16-48` - OpenAI integration and ISTQB prompt
- `app/utils/security.py:7` - SECRET_KEY (needs to be environment variable)
- `app/database/connection.py:5` - Database URL configuration

## Development Notes
- Database tables are auto-created on application startup
- All endpoints except `/health` require authentication via JWT tokens
- OpenAI responses include usage tracking (tokens consumed)
- CORS is fully open for development (should be restricted in production)