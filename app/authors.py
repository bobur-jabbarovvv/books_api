from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from .db_connection import get_database_connection

router = APIRouter()
conn = get_database_connection()
cursor = conn.cursor()

class Author(BaseModel):
    name: str
    country: str

def author_exists(id: int) -> bool:
    cursor.execute(""" SELECT id
                       FROM authors
                       WHERE id = %s """,
                       (int(id),))

    author = cursor.fetchone()
    if author is None:
        return False
    else:
        return True

# POST

@router.post("/authors")
def create_author(author: Author):
    try:
        cursor.execute(""" INSERT INTO authors (name, country)
                           VALUES (%s, %s)""",
                           (author.name, author.country))
        conn.commit()
        return {"data": "Author created successfully"}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# GET

@router.get("/authors")
def get_authors():
    try:
        cursor.execute(""" SELECT *
                           FROM authors
                           ORDER BY id""")
        authors = cursor.fetchall()
        return {"authors": authors}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.get("/authors/country={country}")
def get_authors_by_country(country: str):
    try:
        cursor.execute(""" SELECT *
                           FROM authors
                           WHERE country = %s""",
                           (country,))
        authors = cursor.fetchall()
        return {"authors": authors}

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.get("/authors/{id}")
def get_authors_by_id(id: int):
    try:
        cursor.execute(""" SELECT authors.id as id,
                                  authors.name as name,
                                  authors.country as country,
                                  json_agg(json_build_object('id', books.id,
                                                             'name', books.name)) as books
                           FROM authors
                           JOIN books ON authors.id = books.author_id
                           WHERE authors.id = %s
                           GROUP BY authors.id,
                                    authors.name,
                                    authors.country""",
                           (id,))
        author = cursor.fetchone()
        if author is None:
            raise HTTPException(status_code=404,
                                detail="Author not found")
        return {"author": author}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# PUT

@router.put("/authors/{id}")
def update_author(id: int, author: Author):
    try:
        if author_exists(id):
            cursor.execute(""" UPDATE authors
                               SET name = %s,
                                   country = %s
                               WHERE id = %s""",
                               (author.name,
                                author.country,
                                str(id)))
            conn.commit()
            return {"data": "Author updated successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Author not found")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# DELETE

@router.delete("/authors/{id}")
def delete_author(id: int):
    try:
        if author_exists(id):
            cursor.execute(""" DELETE FROM authors
                               WHERE id = %s""",
                               (int(id),))
            conn.commmit()
            return {"data": "User deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Author not found")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


