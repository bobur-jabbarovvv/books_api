from fastapi import FastAPI, Response, status, HTTPException, Request
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from .db_connection import get_database_connection
from .books import router as books_router
from .users import router as users_router
from .authors import router as authors_router
from .likes import router as likes_router
from .orders import router as orders_router
from .login import router as login_router

app = FastAPI()
conn = get_database_connection()
cursor = conn.cursor()

app.include_router(books_router)
app.include_router(users_router)
app.include_router(authors_router)
app.include_router(likes_router)
app.include_router(orders_router)
app.include_router(login_router)


