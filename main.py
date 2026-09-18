from fastapi import FastAPI

from database import create_db_tables

from routers import auth,users,tasks
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
create_db_tables()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)