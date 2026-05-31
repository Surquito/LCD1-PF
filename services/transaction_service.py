from database.connection import get_connection
from models.transaction import Transaction

# Insertar transacción
def insert_transaction(txn: Transaction):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tbl_transactions 
        (description, amount, type_txn, id_user, id_category)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        txn.description,
        txn.amount,
        txn.type_txn,
        txn.id_user,
        txn.id_category
    ))

    conn.commit()
    conn.close()


# Reporte agrupado por categoría
def get_report_by_category():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.description, SUM(t.amount)
        FROM tbl_transactions t
        JOIN tbl_category c ON t.id_category = c.id_category
        GROUP BY c.description
        ORDER BY SUM(t.amount) DESC
    """)

    result = cursor.fetchall()
    conn.close()

    return result