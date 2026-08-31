from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from db import connect_users_db

router = APIRouter()


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


@router.post("/register")
def register_user(user: User):
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username,email,password) VALUES (?,?,?)",
        (user.username, user.email, user.password),
    )
    conn.commit()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchone()
    for x in users:
        print(dict(users))
    conn.close()
    return user
