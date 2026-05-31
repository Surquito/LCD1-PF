from database.connection import get_connection
from models.user import User

# Crear usuario
def create_user(user: User):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tbl_users (username, password)
        VALUES (%s, %s)
        RETURNING id_user
    """, (user.username, user.password))

    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return user_id


# Login básico
def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_user, username
        FROM tbl_users
        WHERE username = %s AND password = %s
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    return user  # None si no existe