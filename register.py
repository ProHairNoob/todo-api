from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import bcrypt

from db import connect_users_db

router = APIRouter()


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


@router.post("/register")
def register_user(user: User):
    password = user.password.encode("utf-8")
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", ("koko",))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    cursor.execute(
        "INSERT INTO users (username,email,password) VALUES (?,?,?)",
        (user.username, user.email, hashed),
    )
    conn.commit()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchone()
    counter = 0
    for u in users:
        counter += 1
        print(u)
    print(f"there are {counter} users")

    conn.close()
    return "User registered successfully"
