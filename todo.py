from pathlib import Path
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from db import connect_db, users_path, tasks_path

router = APIRouter()


class Todo(BaseModel):
    desc: str
    title: str


@router.post("/todos")
def create_task(todo: Todo, authorization: str = Header(...)):
    conn = connect_db(users_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM tokens WHERE token = ?", (authorization,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
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


@router.put("/todos/{task_id}")
def update_task(task_id: int, todo: Todo, authorization: str = Header(...)):
    conn = connect_db(users_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM tokens WHERE token = ?", (authorization,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    if row:
        user_id = row["user_id"]
        conn = connect_db(tasks_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (
                task_id,
                user_id,
            ),
        )
        task = cursor.fetchone()
        if not task:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="404 NOT FOUND"
            )

        cursor.execute(
            "UPDATE tasks SET desc = ?, title = ? WHERE id = ? AND user_id = ?",
            (todo.desc, todo.title, task_id, user_id),
        )
        conn.commit()
        conn.close()
        return {"id": task_id, "desc": todo.desc, "title": todo.title}


@router.delete("/todos/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tasks(task_id: int, authorization: str = Header(...)):
    conn = connect_db(users_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM tokens WHERE token = ?", (authorization,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    user_id = row["user_id"]
    conn = connect_db(tasks_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (
            task_id,
            user_id,
        ),
    )
    task = cursor.fetchone()
    if not task:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    cursor.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (
            task_id,
            user_id,
        ),
    )
    conn.commit()
    conn.close()
