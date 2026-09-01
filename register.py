import bcrypt
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
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    cursor.execute(
        "INSERT INTO users (username,email,password) VALUES (?,?,?)",
        (user.username, user.email, password),
    )
    conn.commit()
    # debug
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    counter = 0
    for u in users:
        counter += 1
    print(f"there are {counter} users")

    conn.close()
    return "User registered successfully"


@router.post("/login")
def user_login(user: User):
    # check if password is valid
    # check if email is valid
    conn = connect_users_db()
    cursor = conn.cursor()
    print(user.email)
    cursor.execute("SELECT password FROM users WHERE email = ?", (user.email,))
    row = cursor.fetchone()
    print(row, hash_password(user.password))
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid email or password"
        )
    if not bcrypt.checkpw(user.password.encode("utf-8"), row[0]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid email or password"
        )
    return "login succesful"
