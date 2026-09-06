from fastapi import APIRouter, Header
from pydantic import BaseModel

router = APIRouter()


class Todo(BaseModel):
    desc: str
    title: str


@router.post("/todos")
def create_task(todo: Todo, authorization: str = Header(...)):
    return todo, authorization
