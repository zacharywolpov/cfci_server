from pydantic import BaseModel, EmailStr


class LoginRequestSchema(BaseModel):
    """
    Simple schema for user login requests.
    """
    email: EmailStr
    password: str