# backend/schemas.py

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # 'öğretmen' veya 'veli'
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    username: str  # email yerine username
    password: str

class Token(BaseModel):
    access_token: str

