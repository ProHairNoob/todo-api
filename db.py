import sqlite3
from pathlib import Path

db_dir = Path("./db")
db_dir.mkdir(parents=True, exist_ok=True)

users_path = Path("db/users.db")

tasks_path = Path("db/tasks.db")

# router = APIRouter()


def connect_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def make_token_db():
    conn = connect_db(users_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tokens(
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE
    )
    """)
    conn.commit()
    conn.close()


def make_users_db():
    conn = connect_db(users_path)
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


def make_tasks_db():
    conn = connect_db(tasks_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks(
        user_id INT,
        id INTEGER PRIMARY KEY,
        desc TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
