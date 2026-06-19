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
def get_report_by_category(id_user, type_txn=None):
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
            WHERE t.id_user = %s AND t.type_txn = %s
            GROUP BY COALESCE(c_parent.description, c_child.description), 
                     CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END
            ORDER BY total DESC
        """, (id_user, type_txn))
    else:
        cursor.execute("""
            SELECT 
                COALESCE(c_parent.description, c_child.description) AS category,
                CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END AS subcategory,
                SUM(t.amount) AS total
            FROM tbl_transactions t
            JOIN tbl_category c_child ON t.id_category = c_child.id_category
            LEFT JOIN tbl_category c_parent ON c_child.id_subcategory = c_parent.id_category
            WHERE t.id_user = %s
            GROUP BY COALESCE(c_parent.description, c_child.description), 
                     CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END
            ORDER BY total DESC
        """, (id_user,))

    result = cursor.fetchall()
    conn.close()

    return result


def get_financial_summary(id_user):
    conn = get_connection()
    if not conn:
        return {
            "total_income": 0.0,
            "total_expense": 0.0,
            "net_balance": 0.0
        }
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type_txn = 'ingreso' THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN type_txn = 'gasto' THEN amount ELSE 0 END), 0) AS total_expense
        FROM tbl_transactions
        WHERE id_user = %s;
    """, (id_user,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    total_income = float(result[0]) if result else 0.0
    total_expense = float(result[1]) if result else 0.0
    net_balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance
    }