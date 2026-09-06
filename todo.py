from fastapi import APIRouter, Header
from pydantic import BaseModel

router = APIRouter()


class Todo(BaseModel):
    desc: str
    title: str


@router.post("/todo")
def create_task(todo: Todo, authorization: str = Header(...)):
    pass
