from pydantic import BaseModel, EmailStr

class UserCreateSchema(BaseModel):
    email: EmailStr
    firstname: str
    lastname: str
    password: str

class UserReadSchema(BaseModel):
    id: int
    email: EmailStr
    firstname: str
    lastname: str

