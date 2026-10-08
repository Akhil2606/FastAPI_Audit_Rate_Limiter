# FastAPI Audit & Rate Limiter

A FastAPI backend project implementing JWT authentication, PostgreSQL database integration, request auditing, rate limiting, exception handling, and admin audit-log management.

## Features

- JWT-based authentication
- HTTP Bearer authentication
- User registration and login
- Password hashing using Argon2
- PostgreSQL database
- SQLAlchemy ORM
- Request audit logging
- IP/user-based rate limiting
- Configurable rate limits using environment variables
- HTTP 429 response when rate limit is exceeded
- Global exception handling
- Admin-only audit-log APIs
- Audit-log filtering
- Pagination
- Automatic deletion of old audit logs
- Health-check endpoint excluded from auditing and rate limiting

## Technologies

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- PyJWT
- pwdlib
- Uvicorn

## Project Structure

```text
app/
├── main.py
├── create_tables.py
├── core/
├── models/
├── schemas/
├── routers/
├── middleware/
└── dependencies/