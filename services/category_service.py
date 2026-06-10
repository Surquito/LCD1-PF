from database.connection import get_connection
from models.category import Category

# Obtener todas las categorías
def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_category, description, id_subcategory, type_category
        FROM tbl_category
    """)

    rows = cursor.fetchall()
    conn.close()

    categorias = []

    for row in rows:
        categoria = Category(
            id_category=row[0],
            description=row[1],
            id_subcategory=row[2],
            type_category=row[3]
        )
        categorias.append(categoria)

    return categorias


# Crear categoría o subcategoría (devuelve el id asignado)
def create_category(category: Category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tbl_category (description, id_subcategory, type_category)
        VALUES (%s, %s, %s)
        RETURNING id_category;
    """, (category.description, category.id_subcategory, category.type_category or 'gasto'))

    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return new_id


# Obtener subcategorías asociadas a una categoría padre
def get_subcategories_by_parent(parent_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_category, description, id_subcategory, type_category
        FROM tbl_category
        WHERE id_subcategory = %s
        ORDER BY description ASC
    """, (parent_id,))

    rows = cursor.fetchall()
    conn.close()

    subcategorias = []
    for row in rows:
        subcat = Category(
            id_category=row[0],
            description=row[1],
            id_subcategory=row[2],
            type_category=row[3]
        )
        subcategorias.append(subcat)

    return subcategorias
