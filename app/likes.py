from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from .db_connection import get_database_connection

router = APIRouter()
conn = get_database_connection()
cursor = conn.cursor()

class Like(BaseModel):
    user_id: int
    book_id: int

# POST

@router.post("/likes")
def create_like(like: Like):
    try:
        cursor.execute(""" INSERT INTO likes (user_id, book_id)
                           VALUES (%s, %s)""",
                           (like.user_id, like.book_id))
        conn.commit()
        return {"message": "Like created successfully"}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# GET

@router.get("/likes")
def get_likes():
    try:
        cursor.execute(""" SELECT users.id as user_id,
                                  users.username as username,
                                  books.id as book_id,
                                  books.name as book_name
                           FROM likes
                           JOIN users ON likes.user_id=users.id
                           JOIN books on likes.book_id=books.id""")
        likes = cursor.fetchall()
        return {"likes": likes}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.get("/likes/{user_id}/")
def get_likes_of_user(user_id: int):
    try:
        cursor.execute(""" SELECT users.id as user_id,
                                  users.username as username,
                                  books.id as book_id,
                                  books.name as book_name
                           FROM likes
                           JOIN users ON likes.user_id = users.id
                           JOIN books ON likes.book_id = books.id
                           WHERE user_id = %s """,
                           (str(user_id),))
        like = cursor.fetchone()
        if like is None:
            raise HTTPException(status_code=400,
                                detail="Like not found")
        return {"like": like}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.delete("/likes/{user_id}/{book_id}")
def delete_like(user_id: int, book_id: int):
    try:
        cursor.execute(""" DELETE FROM likes
                           WHERE user_id = %s AND book_id = %s""",
                           (str(user_id), str(book_id),))
        conn.commit()
        return {"message": "Like deleted successfully"}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))
