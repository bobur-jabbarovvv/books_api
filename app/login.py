from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
import hashlib
from .db_connection import get_database_connection

router = APIRouter()
conn = get_database_connection()
cursor = conn.cursor()

class Login(BaseModel):
    username: str
    password: str

class Logout(BaseModel):
    username: str

@router.post("/login")
def login_user(login_data: Login):
    try:
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(login_data.password.encode()).hexdigest()
        cursor.execute(""" SELECT *
                           FROM users
                           WHERE username = %s AND password = %s """,
                           (login_data.username, hashed_password))
        user = cursor.fetchone()

        if user:
            cursor.execute(""" UPDATE users
                               SET logged_in = true
                               WHERE username = %s """,
                               (login_data.username,))
            conn.commit()
            cursor.close()
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid username or password")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.post("/logout")
def logout(logout_data: Logout):
    try:
        cursor = conn.cursor()
        cursor.execute(""" SELECT *
                           FROM users
                           WHERE username = %s """,
                           (logout_data.username,))
        user = cursor.fetchone()

        if user:
            cursor.execute(""" UPDATE users
                               SET logged_in = false
                               WHERE username = %s """,
                               (logout_data.username,))
            conn.commit()
            cursor.close()
            return {"message": "Logout successful"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid username or password")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))




