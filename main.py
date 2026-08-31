import uvicorn
from fastapi import FastAPI

from db import make_users_db
from register import router as register_router

# Init db
make_users_db()


app = FastAPI()

app.include_router(register_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
