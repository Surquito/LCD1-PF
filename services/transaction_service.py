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


# Reporte agrupado por categoría y subcategoría
def get_report_by_category(type_txn=None):
    conn = get_connection()
    cursor = conn.cursor()

    if type_txn:
        cursor.execute("""
            SELECT 
                COALESCE(c_parent.description, c_child.description) AS category,
                CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END AS subcategory,
                SUM(t.amount) AS total
            FROM tbl_transactions t
            JOIN tbl_category c_child ON t.id_category = c_child.id_category
            LEFT JOIN tbl_category c_parent ON c_child.id_subcategory = c_parent.id_category
            WHERE t.type_txn = %s
            GROUP BY COALESCE(c_parent.description, c_child.description), 
                     CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END
            ORDER BY total DESC
        """, (type_txn,))
    else:
        cursor.execute("""
            SELECT 
                COALESCE(c_parent.description, c_child.description) AS category,
                CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END AS subcategory,
                SUM(t.amount) AS total
            FROM tbl_transactions t
            JOIN tbl_category c_child ON t.id_category = c_child.id_category
            LEFT JOIN tbl_category c_parent ON c_child.id_subcategory = c_parent.id_category
            GROUP BY COALESCE(c_parent.description, c_child.description), 
                     CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END
            ORDER BY total DESC
        """)

    result = cursor.fetchall()
    conn.close()

    return result