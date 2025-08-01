# User Stories

## 1. Register a User
- **Persona**: New user
- **Story Statement**: As a new user, I want to register an account so that I can access the ISTQB Assistant features.
- **Benefit**: Secure access to the assistant with personalized user management.
- **Acceptance Criteria**:
  - User can register with a unique email and username.
  - Registration fails if email or username already exists.
- **Mapped Endpoint**: `POST /auth/register`

## 2. Authenticate and Login
- **Persona**: Registered user
- **Story Statement**: As a registered user, I want to log in to access the ISTQB Assistant's functionality.
- **Benefit**: Authentication for personalized experiences and security.
- **Acceptance Criteria**:
  - User receives a JWT token upon successful login.
  - Access token is provided for authenticated access.
- **Mapped Endpoint**: `POST /auth/login`

## 3. Chat with ISTQB Assistant
- **Persona**: Registered user
- **Story Statement**: As a user, I want to ask questions about software testing concepts and receive intelligent answers.
- **Benefit**: Expedited learning and assistance on software testing matters.
- **Acceptance Criteria**:
  - User receives coherent and precise answers about ISTQB topics.
  - Option to include context and certification code in queries.
- **Mapped Endpoint**: `POST /chat/`

## 4. Upload Certification Documents
- **Persona**: Admin user
- **Story Statement**: As an admin, I want to upload syllabus and sample exam documents for certifications.
- **Benefit**: Maintain and update certification materials.
- **Acceptance Criteria**:
  - Admin can upload PDF documents.
  - Duplicate documents are recognized and alerts provided.
- **Mapped Endpoint**: `POST /certifications/{certification_id}/documents/syllabus`
  - **Alternative Endpoint**: `POST /certifications/{certification_id}/documents/sample-exam`

## 5. Manage Certifications
- **Persona**: Admin user
- **Story Statement**: As an admin, I want to view, create, and manage certifications easily.
- **Benefit**: Centralized management of certification data.
- **Acceptance Criteria**:
  - Able to create new certification entries.
  - Option to soft delete certifications.
  - Listings include all active certifications.
- **Mapped Endpoint**: `POST /certifications/`
  - **View Certifications**: `GET /certifications/`
  - **Delete Certification**: `DELETE /certifications/{certification_id}`

