from database.connection import get_connection
from models.category import Category

# Obtener todas las categorías
def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_category, description, id_subcategory
        FROM tbl_category
    """)

    rows = cursor.fetchall()
    conn.close()

    categorias = []

    for row in rows:
        categoria = Category(
            id_category=row[0],
            description=row[1],
            id_subcategory=row[2]
        )
        categorias.append(categoria)

    return categorias


# Crear categoría
def create_category(category: Category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tbl_category (description, id_subcategory)
        VALUES (%s, %s)
    """, (category.description, category.id_subcategory))

    conn.commit()
    conn.close()
