# CFCI Server API Reference

This document describes the main authentication and chat endpoints, including exact JSON request and response formats.

## Authentication Endpoints (`/api/auth`)

### Register User
- **POST** `/api/auth/register`
- **Request Body:**
```json
{
  "email": "user@example.com",
  "firstname": "John",
  "lastname": "Doe",
  "password": "yourpassword"
}
```
- **Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "firstname": "John",
  "lastname": "Doe"
}
```

### Login
- **POST** `/api/auth/login`
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```
- **Response:**
```json
{
  "user_id": 1,
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

---

## Chat Endpoints (`/api/chat`)

### Initiate Chat
- **POST** `/api/chat/initiate`
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Request Body:**
  - _None_
- **Response:**
```json
{
  "conversation_id": 123,
  "message_id": 456,
  "message_num": 0,
  "sender": "agent",
  "content": "Hi! I'm an AI assistant here to help you with your questions about the Christenson Family Center for Innovation. How can I assist you today?"
}
```

### Advance Chat
- **POST** `/api/chat/advance`
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Request Body:**
```json
{
  "conversation_id": 123,
  "user_message": "Tell me about the center.",
  "message_step_num": 1
}
```
- **Response:**
```json
{
  "message_id": 789,
  "message_num": 2,
  "sender": "agent",
  "content": "The Christenson Family Center for Innovation is ..."
}
```

---

## Notes
- All endpoints return standard HTTP error codes for invalid input or authentication errors.
- The `access_token` is required for all chat endpoints and should be obtained via the login endpoint.
- Field names and types are strictly enforced as shown above.
- For more details on the chat flow, see the code in `app/api/chat.py`.
