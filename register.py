import bcrypt
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from auth import hash_password, create_token
from db import connect_db

router = APIRouter()

user_path = Path("./db/users.db")


class sign_up_user(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)


class login_user(BaseModel):
    email: EmailStr
    password: str


def validate_login(row, password):
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid email or password"
        )
    if not bcrypt.checkpw(password.encode("utf-8"), row["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid email or password"
        )


@router.post("/register")
def register_user(user: sign_up_user):
    password = hash_password(user.password)
    conn = connect_db(user_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )
    cursor.execute("SELECT 1 FROM users WHERE email = ?", (user.email,))
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
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (user.email,))
    row = cursor.fetchone()
    user_id = row["user_id"]
    token = create_token()
    cursor.execute("INSERT INTO tokens (token,user_id) VALUES (?,?)", (token, user_id))
    conn.commit()
    conn.close()
    json_token = {"token": token, "user_id": user_id}

    return json_token


@router.post("/login")
def user_login(user: login_user):
    # check if password is valid
    # check if email is valid
    conn = connect_db(user_path)
    cursor = conn.cursor()
    cursor.execute("SELECT password ,user_id FROM users WHERE email = ?", (user.email,))
    row = cursor.fetchone()
    validate_login(row, user.password)
    user_id = row["user_id"]
    token = create_token()
    cursor.execute("INSERT INTO tokens (token,user_id) VALUES (?,?)", (token, user_id))
    conn.commit()
    conn.close()

    json_token = {"token": token, "user_id": user_id}
    return json_token
