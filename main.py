import sqlite3
import datetime
from transformers import pipeline
import warnings

# Ocultar advertencias de la librería Transformers para una consola más limpia
warnings.filterwarnings("ignore")

# ==========================================
# 1. MODELOS DE DATOS (POO)
# ==========================================
class Ingreso:
    def __init__(self, monto, descripcion):
        self.__monto = float(monto)
        self.__descripcion = descripcion
        self.__fecha = datetime.date.today().strftime("%Y-%m-%d")

    def get_monto(self):
        return self.__monto

    def get_descripcion(self):
        return self.__descripcion

    def get_fecha(self):
        return self.__fecha

    def __str__(self):
        return f"[{self.__fecha}] S/.{self.__monto} - {self.__descripcion}"


class Gasto:
    def __init__(self, monto, descripcion):
        self.__monto = float(monto)
        self.__descripcion = descripcion
        self.__fecha = datetime.date.today().strftime("%Y-%m-%d")
        self.__categoria = None
        self.__subcategoria = None

    def get_monto(self):
        return self.__monto

    def get_descripcion(self):
        return self.__descripcion

    def get_fecha(self):
        return self.__fecha

    def get_categoria(self):
        return self.__categoria

    def get_subcategoria(self):
        return self.__subcategoria

    def set_categoria(self, categoria):
        self.__categoria = categoria

    def set_subcategoria(self, subcategoria):
        self.__subcategoria = subcategoria

    def __str__(self):
        return f"[{self.__fecha}] S/.{self.__monto} - {self.__descripcion} ({self.__categoria} -> {self.__subcategoria})"



# ==========================================
# 2. MÓDULO DE INTELIGENCIA ARTIFICIAL (NLP)
# ==========================================
class ClasificadorIA:
    def __init__(self):
        print("\n[Sistema] Cargando modelo de Inteligencia Artificial...")
        self.clasificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        self.categorias = [
            "Alimentación y Comida",
            "Transporte y Pasajes",
            "Educación y Estudios",
            "Entretenimiento y Ocio",
            "Salud y Farmacia",
            "Hogar y Servicios"
        ]
        self.subcategorias = {
            "Alimentación y Comida": ["Restaurantes", "Supermercado", "Snacks y Delivery"],
            "Transporte y Pasajes": ["Taxi / Colectivo", "Pasajes / Transporte Público", "Combustible y Auto"],
            "Educación y Estudios": ["Mensualidades y Cursos", "Libros y Materiales", "Otros Estudios"],
            "Entretenimiento y Ocio": ["Cine y Eventos", "Hobbies", "Suscripciones y Juegos"],
            "Salud y Farmacia": ["Consultas Médicas", "Medicamentos", "Seguros y Exámenes"],
            "Hogar y Servicios": ["Alquiler / Hipoteca", "Servicios (Luz, Agua, Internet)", "Mantenimiento y Hogar"]
        }

    def categorizar_gasto(self, descripcion):
        res_cat = self.clasificador(descripcion, self.categorias)
        cat = res_cat['labels'][0]
        subcats = self.subcategorias.get(cat, ["Otros"])
        res_sub = self.clasificador(descripcion, subcats)
        subcat = res_sub['labels'][0]
        return cat, subcat



# ==========================================
# 3. PERSISTENCIA DE DATOS (SQLite)
# ==========================================
class BaseDeDatos:
    def __init__(self, nombre_db="finanzas.db"):
        self.nombre_db = nombre_db
        self.crear_tabla()

    def conectar(self):
        return sqlite3.connect(self.nombre_db)

    def crear_tabla(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT NOT NULL,
                subcategoria TEXT NOT NULL DEFAULT 'Otros'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_ingresos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                monto REAL NOT NULL
            )
        ''')
        try:
            cursor.execute("SELECT subcategoria FROM registro_gastos LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE registro_gastos ADD COLUMN subcategoria TEXT NOT NULL DEFAULT 'Otros'")
        conexion.commit()
        conexion.close()

    def insertar_gasto(self, gasto):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO registro_gastos (fecha, descripcion, monto, categoria, subcategoria)
            VALUES (?, ?, ?, ?, ?)
        ''', (gasto.get_fecha(), gasto.get_descripcion(), gasto.get_monto(), gasto.get_categoria(), gasto.get_subcategoria()))
        conexion.commit()
        conexion.close()
        print("[Base de Datos] Gasto guardado exitosamente.")

    def insertar_ingreso(self, ingreso):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO registro_ingresos (fecha, descripcion, monto)
            VALUES (?, ?, ?)
        ''', (ingreso.get_fecha(), ingreso.get_descripcion(), ingreso.get_monto()))
        conexion.commit()
        conexion.close()
        print("[Base de Datos] Ingreso guardado exitosamente.")

    def obtener_total_ingresos(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT SUM(monto) FROM registro_ingresos")
        res = cursor.fetchone()[0]
        conexion.close()
        return res if res is not None else 0.0

    def obtener_total_gastos(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT SUM(monto) FROM registro_gastos")
        res = cursor.fetchone()[0]
        conexion.close()
        return res if res is not None else 0.0

    def generar_reporte_gastos(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute('''
            SELECT categoria, subcategoria, SUM(monto) as total
            FROM registro_gastos
            GROUP BY categoria, subcategoria
            ORDER BY total DESC
        ''')
        resultados = cursor.fetchall()
        conexion.close()
        return resultados


# ==========================================
# 4. INTERFAZ Y LÓGICA PRINCIPAL (main)
def main():
    print("="*50)
    print(" ASISTENTE INTELIGENTE DE FINANZAS PERSONALES ")
    print("="*50)

    bd = BaseDeDatos()
    
    try:
        ia = ClasificadorIA()
    except Exception as e:
        print(f"\n[Error] No se pudo cargar el modelo de IA: {e}")
        return

    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Registrar un nuevo ingreso")
        print("2. Registrar un nuevo gasto")
        print("3. Ver reporte financiero")
        print("4. Salir")
        
        opcion = input("Selecciona una opción (1-4): ")

        if opcion == '1':
            try:
                monto = float(input("\nIngresa el monto del ingreso: S/."))
                desc = input("Describe el origen del ingreso: ")
                nuevo_ingreso = Ingreso(monto, desc)
                bd.insertar_ingreso(nuevo_ingreso)
            except ValueError:
                print("\n[Error] El monto debe ser un número.")

        elif opcion == '2':
            try:
                monto = float(input("\nIngresa el monto gastado: S/."))
                desc = input("Describe en qué gastaste el dinero: ")
                nuevo_gasto = Gasto(monto, desc)
                
                cat, subcat = ia.categorizar_gasto(nuevo_gasto.get_descripcion())
                nuevo_gasto.set_categoria(cat)
                nuevo_gasto.set_subcategoria(subcat)
                
                print(f"-> La IA clasificó tu gasto como: '{cat}' > '{subcat}'")
                bd.insertar_gasto(nuevo_gasto)
            except ValueError:
                print("\n[Error] El monto debe ser un número.")

        elif opcion == '3':
            print("\n--- RESUMEN FINANCIERO ---")
            total_ingresos = bd.obtener_total_ingresos()
            total_gastos = bd.obtener_total_gastos()
            balance = total_ingresos - total_gastos
            
            print(f"Total Ingresos: S/. {total_ingresos:.2f}")
            print(f"Total Gastos:   S/. {total_gastos:.2f}")
            print(f"Balance Neto:   S/. {balance:.2f}")
            print("-" * 62)
            
            reporte_gastos = bd.generar_reporte_gastos()
            if not reporte_gastos:
                print("No hay gastos registrados.")
            else:
                print(f"{'CATEGORÍA':<20} | {'SUBCATEGORÍA':<20} | {'TOTAL (S/.)':<10}")
                print("-" * 62)
                for fila in reporte_gastos:
                    cat, subcat, total = fila
                    print(f"{cat:<20} | {subcat:<20} | S/. {total:.2f}")
                print("-" * 62)

        elif opcion == '4':
            print("\n¡Hasta luego!")
            break
        else:
            print("\n[Error] Opción no válida.")


if __name__ == "__main__":
    main()