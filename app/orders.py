from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from .db_connection import get_database_connection

router = APIRouter()
conn = get_database_connection()
cursor = conn.cursor()

class Order(BaseModel):
    user_id: int
    book_id: int

# POST

@router.post("/orders")
def create_order(order: Order):
    try:
        cursor.execute(""" INSERT INTO orders
                           (user_id, book_id)
                           VALUES (%s, %s)""",
                           (order.user_id, order.book_id))
        conn.commit()
        return {"data": "Order created successfully"}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# GET

@router.get("/orders")
def get_orders():
    try:
        cursor.execute(""" SELECT users.id as user_id,
                                  users.username,
                                  books.id as book_id,
                                  books.name,
                                  ordered_at
                           FROM orders
                           JOIN users ON orders.user_id = users.id
                           JOIN books ON orders.book_id = books.id """)
        orders = cursor.fetchall()
        return {"orders": orders}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

@router.get("/orders/{user_id}")
def get_orders_of_user(user_id: int):

    try:
        cursor.execute(""" SELECT users.id as user_id,
                                  users.username as username,
                                  books.id as book_id,
                                  books.name as book_name,
                                  ordered_at
                           FROM orders
                           JOIN users ON orders.user_id = users.id
                           JOIN books ON orders.book_id = books.id
                           WHERE user_id = %s """,
                           (str(user_id),))
        order = cursor.fetchone()

        if order is None:
            raise HTTPException(status_code=400,
                                detail="Order not found")
        return {"order": order}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# PUT

@router.put("/orders/{user_id}/{book_id}")
def update_order(order: Order, user_id: int, book_id: int):

    try:
        cursor.execute(""" UPDATE orders
                           SET user_id = %s, book_id = %s
                           WHERE user_id = %s AND book_id = %s""",
                           (order.user_id, order.book_id, str(user_id), str(book_id)))
        conn.commit()
        return {"data": "Order updated successfully"}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))

# DELETE

@router.delete("/orders/{user_id}/{book_id}")
def delete_order(user_id: int, book_id: int):
    try:
        cursor.execute("""DELETE FROM orders
                          WHERE user_id = %s AND book_id = %s""",
                          (str(user_id), str(book_id),))
        conn.commit()
        return {"data": "Order deleted successfully"}

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))
