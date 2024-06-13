from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
import hashlib
from .db_connection import get_database_connection

router = APIRouter()
conn = get_database_connection()
cursor = conn.cursor()

class User(BaseModel):
    username: str
    password: str
    address: str
    phone_number: str
    logged_in: bool = False

def user_exist(id: int) -> bool:
    cursor.execute(""" SELECT id
                       FROM users
                       WHERE id = %s """,
                       (int(id),))
    user = cursor.fetchone()
    if user is None:
        return False
    else:
        return True

# POST

@router.post("/users")
def create_user(user: User):
    try:
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        cursor.execute(""" INSERT INTO users
                           (username, password, address, phone_number)
                           VALUES (%s, %s, %s, %s) """,
                           (user.username, hashed_password, user.address, user.phone_number))
        conn.commit()
        return {"data": "User created successfully"}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# GET

@router.get("/users")
def get_users():
    try:
        cursor.execute(""" SELECT *
                           FROM users""")
        users = cursor.fetchall()
        return {"users": users}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.get("/users/{identifier}")
def get_user_by_id(identifier: int):
    try:
        cursor.execute(""" SELECT *
                           FROM users
                           WHERE id = %s """,
                           (int(identifier),))

        user = cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404,
                                detail="User not found")
        return {"user": user}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# PUT

@router.put("/users/{id}")
def update_user(id: int, user: User):
    try:
        if user_exist(id):
            hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
            cursor.execute(""" UPDATE users
                               SET username = %s,
                                   password = %s,
                                   address = %s,
                                   phone_number = %s
                               WHERE id = %s """,
                               (user.username, hashed_password, user.address, user.phone_number, int(id)))
            conn.commit()
            return {"data": "User updated successfully"}
        else:
            raise HTTPException(status_code=404,
                                detail="User not found")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# DELETE

@router.delete("/users/{id}")
def delete_user(id: int):
    try:
        if user_exist(id):
            cursor.execute(""" DELETE
                               FROM users
                               WHERE id = %s """,
                               str(id))
            conn.commit()
            return {"data": "User deleted successfully"}

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))



