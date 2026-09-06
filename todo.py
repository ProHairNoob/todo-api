from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Todo(BaseModel):
    desc: str
    title: str
