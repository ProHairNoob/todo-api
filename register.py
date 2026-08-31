from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, secretStr

router = APIRouter()


class User(BaseModel):
    username: str
    email: EmailStr
    password: secretStr


@router.post("/register")
def register_user(user: User):
    return user
