from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from auth import hash_password
from db import connect_users_db

router = APIRouter()


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


@router.post("/register")
def register_user(user: User):
    password = hash_password(user.password)
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (user.username,))
    print(cursor.fetchall())
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    cursor.execute(
        "INSERT INTO users (username,email,password) VALUES (?,?,?)",
        (user.username, user.email, password),
    )
    conn.commit()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    counter = 0
    for u in users:
        counter += 1
    print(f"there are {counter} users")

    conn.close()
    return "User registered successfully"
