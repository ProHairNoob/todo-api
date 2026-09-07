from pathlib import Path
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from db import connect_db

router = APIRouter()

user_path = Path("./db/users.db")
tasks_path = Path("./db/tasks.db")


class Todo(BaseModel):
    desc: str
    title: str


# todo add creating the tasks by authorizing if the token exists in the database


@router.post("/todos")
def create_task(todo: Todo, authorization: str = Header(...)):
    conn = connect_db(user_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM tokens WHERE token = ?", (authorization,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_id = row["user_id"]

        conn = connect_db(tasks_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (user_id,desc,title) VALUES (?,?,?)",
            (user_id, todo.desc, todo.title),
        )
        conn.commit()
        conn.close()
        return {"id": cursor.lastrowid, "desc": todo.desc, "title": todo.title}
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
