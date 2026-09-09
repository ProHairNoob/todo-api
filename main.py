import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import make_token_db, make_users_db, make_tasks_db
from register import router as register_router
from todo import router as task_router

# Init db
make_users_db()
make_token_db()
make_tasks_db()

app = FastAPI()

app.include_router(register_router)
app.include_router(task_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "todos.html")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning",
        access_log=False,
    )
