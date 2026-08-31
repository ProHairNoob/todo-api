from pathlib import Path
import sqlite3


db_dir = Path("./db")
db_dir.mkdir(parents=True, exist_ok=True)

users_path = Path("db/users.db")
tasks_path = Path("db/tasks.db")

# router = APIRouter()


def connect_users_db():
    conn = sqlite3.connect(users_path)
    conn.row_factory = sqlite3.Row
    return conn


def make_users_db():
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def connect_tasks_db():
    conn = sqlite3.connect(tasks_path)
    conn.row_factory = sqlite3.Row
    return conn


def make_tasks_db():
    conn = connect_tasks_db()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks(
        user_id INTEGER PRIMARY KEY,
        id INTEGER PRIMARY KEY,
        desc TEXT NOT NULL,
    )
    """)
