# Authentication API – PlaceMind AI

## Base URL
http://localhost:8000

---

## 1. Register
POST /auth/register

Body:
{
  "email": "user@example.com",
  "password": "string",
  "role": "student | coordinator"
}

Response:
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}

---

## 2. Login
POST /auth/login

Body:
{
  "email": "user@example.com",
  "password": "string"
}

Response:
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}

---

## 3. Refresh Token
POST /auth/refresh

Body:
{
  "refresh_token": "jwt"
}

Response:
{
  "access_token": "new_jwt",
  "token_type": "bearer"
}
