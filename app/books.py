from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import List
from .db_connection import get_database_connection

router = APIRouter()
conn = get_database_connection()
cursor = conn.cursor()

class Book(BaseModel):
    name: str
    author_id: int
    price: float
    genres: str
    liked: int = 0
    ordered: int = 0
    on_sale: bool = True

def book_exists(id: int) -> bool:
    cursor.execute(""" SELECT id
                       FROM books
                       WHERE id = %s """,
                       (int(id),))
    book = cursor.fetchone()

    if book is None:
        return False
    else:
        return True

# POST

@router.post("/books")
def create_book(book: Book):

    try:
        cursor.execute(""" INSERT INTO books (name, author_id, price, genres)
                           VALUES (%s, %s, %s, %s)
                           RETURNING id """,
                           (book.name, book.author_id, book.price, book.genres))
        conn.commit()
        return {"data": "Book created successfully"}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))
    
# GET

@router.get("/books")
def get_books():
    try:
        cursor.execute(""" SELECT books.id,
                                  books.name,
                                  author_id,
                                  authors.name as author,
                                  authors.country as author_country,
                                  price,
                                  genres,
                                  liked,
                                  ordered,
                                  on_sale,
                                  COUNT(likes.book_id) as liked,
                                  COUNT(orders.book_id) as ordered
                           FROM books
                           JOIN authors ON books.author_id = authors.id
                           LEFT JOIN likes ON books.id = likes.book_id
                           LEFT JOIN orders ON books.id = orders.book_id
                           GROUP BY books.id, books.name, author_id, authors.name, authors.country, price, liked, ordered, on_sale
                           ORDER BY books.id """)
        books = cursor.fetchall()
        return {"books": books}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.get("/books/{id}")
def get_book_by_id(id: int):
    try:
        cursor.execute("""SELECT books.id,
                                 books.name,
                                 books.author_id,
                                 authors.name as author,
                                 authors.country as author_country,
                                 books.price,
                                 books.genres,
                                 books.liked,
                                 books.ordered,
                                 books.on_sale,
                                 COUNT(likes.book_id) as liked,
                                 COUNT(orders.book_id) as ordered
                          FROM books
                          JOIN authors ON books.author_id = authors.id
                          LEFT JOIN likes ON books.id = likes.book_id
                          LEFT JOIN orders ON books.id = orders.book_id
                          WHERE books.id = %s 
                          GROUP BY books.id, authors.id """,
                          (id,))
        book = cursor.fetchone()

        if book is None:
            raise HTTPException(status_code=404,
                                detail="Book not found")
        return {"book": book}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.get("/genres={genres}")
def get_books_by_genre(genres: str):
    try:
        cursor.execute(""" SELECT books.id,
                                  books.name,
                                  author_id,
                                  authors.name as author,
                                  authors.country as author_country,
                                  price,
                                  genres,
                                  liked,
                                  ordered,
                                  on_sale,
                                  COUNT(likes.book_id) as liked,
                                  COUNT(orders.book_id) as ordered
                           FROM books
                           JOIN authors ON books.author_id = authors.id
                           LEFT JOIN likes ON books.id = likes.book_id
                           LEFT JOIN orders ON books.id = orders.book_id
                           WHERE genres ILIKE %s 
                           GROUP BY books.id, books.name, author_id, authors.name, authors.country, price, liked, ordered, on_sale
                           ORDER BY books.id """,
                           ('%' + genres + '%',))
        genres = cursor.fetchall()
        return {"genres": genres}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.put("/books/{id}")
def update_book(book: Book, id: int):
    try:
        if book_exists(id):
            cursor.execute(""" UPDATE books
                               SET name = %s,
                                   author_id = %s,
                                   price = %s,
                                   genres = %s
                               WHERE id = %s """,
                               (book.name,
                                book.author_id,
                                book.price,
                                book.genres,
                                str(id),))

            conn.commit()
            return {"data": "Book updated successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Book not found")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# DELETE

@router.delete("/books/{id}")
def delete_book(id: int):
    try:
        if book_exists(id):
            cursor.execute(""" DELETE FROM books
                               WHERE id = %s
                               RETURNING * """,
                               (str(id),))
            conn.commit()
            return {"data": "Book deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Book not found")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))