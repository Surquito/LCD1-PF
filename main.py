import sqlite3
import datetime
from transformers import pipeline
import warnings

# Ocultar advertencias de la librería Transformers para una consola más limpia
warnings.filterwarnings("ignore")

# ==========================================
# 1. PROGRAMACIÓN ORIENTADA A OBJETOS (POO)
# ==========================================
class Gasto:
    def __init__(self, monto, descripcion):
        """Inicializa un gasto con monto, descripción, fecha actual y categoría vacía."""
        self.__monto = float(monto) # Encapsulación básica
        self.__descripcion = descripcion
        self.__fecha = datetime.date.today().strftime("%Y-%m-%d")
        self.__categoria = None

    # Getters
    def get_monto(self):
        return self.__monto
    
    def get_descripcion(self):
        return self.__descripcion
    
    def get_fecha(self):
        return self.__fecha
    
    def get_categoria(self):
        return self.__categoria
    
    # Setter
    def set_categoria(self, categoria):
        self.__categoria = categoria

    def __str__(self):
        return f"[{self.__fecha}] S/.{self.__monto} - {self.__descripcion} (Cat: {self.__categoria})"


# ==========================================
# 2. MÓDULO DE INTELIGENCIA ARTIFICIAL (NLP)
# ==========================================
class ClasificadorIA:
    def __init__(self):
        print("\n[Sistema] Cargando modelo de Inteligencia Artificial (Hugging Face)...")
        print("[Sistema] Esto puede tardar unos segundos la primera vez.")
        # Usamos Zero-Shot Classification para categorizar texto sin entrenamiento previo
        # Se usa el modelo multilingüe para que entienda español
        self.clasificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        
        # Definimos las categorías financieras posibles
        self.categorias_candidatas = [
            "Alimentación y Comida", 
            "Transporte y Pasajes", 
            "Educación y Estudios", 
            "Entretenimiento y Ocio", 
            "Salud y Farmacia",
            "Hogar y Servicios"
        ]

    def categorizar_gasto(self, descripcion):
        """Analiza la descripción y retorna la categoría más probable."""
        print("\n[IA] Analizando el gasto...")
        resultado = self.clasificador(descripcion, self.categorias_candidatas)
        # Retorna la categoría con el score (probabilidad) más alto
        categoria_predicha = resultado['labels'][0]
        return categoria_predicha


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
        """Crea la tabla si no existe en la base de datos."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT NOT NULL
            )
        ''')
        conexion.commit()
        conexion.close()

    def insertar_gasto(self, gasto):
        """Inserta un objeto Gasto en la base de datos usando DML."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO registro_gastos (fecha, descripcion, monto, categoria)
            VALUES (?, ?, ?, ?)
        ''', (gasto.get_fecha(), gasto.get_descripcion(), gasto.get_monto(), gasto.get_categoria()))
        conexion.commit()
        conexion.close()
        print("[Base de Datos] Gasto guardado exitosamente.")

    def generar_reporte_agrupado(self):
        """Realiza una consulta SELECT agrupada por categoría."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute('''
            SELECT categoria, SUM(monto) as total
            FROM registro_gastos
            GROUP BY categoria
            ORDER BY total DESC
        ''')
        resultados = cursor.fetchall()
        conexion.close()
        return resultados


# ==========================================
# 4. INTERFAZ Y LÓGICA PRINCIPAL (main)
# ==========================================
def main():
    print("="*50)
    print(" ASISTENTE INTELIGENTE DE FINANZAS PERSONALES ")
    print("="*50)

    # Inicializar componentes
    bd = BaseDeDatos()
    
    # Manejo de excepciones al cargar el modelo
    try:
        ia = ClasificadorIA()
    except Exception as e:
        print(f"\n[Error Crítico] No se pudo cargar el modelo de IA: {e}")
        print("Asegúrate de tener instalada la librería: pip install transformers torch")
        return

    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Registrar un nuevo gasto")
        print("2. Ver reporte de gastos por categoría")
        print("3. Salir")
        
        opcion = input("Selecciona una opción (1-3): ")

        if opcion == '1':
            try:
                monto_input = float(input("\nIngresa el monto gastado (Ej. 35.50): S/."))
                desc_input = input("Describe en qué gastaste el dinero: ")
                
                # 1. Crear el objeto
                nuevo_gasto = Gasto(monto_input, desc_input)
                
                # 2. Inteligencia artificial predice la categoría
                categoria_asignada = ia.categorizar_gasto(nuevo_gasto.get_descripcion())
                nuevo_gasto.set_categoria(categoria_asignada)
                
                print(f"-> La IA clasificó tu gasto como: '{categoria_asignada}'")
                
                # 3. Guardar en Base de Datos
                bd.insertar_gasto(nuevo_gasto)
                
            except ValueError:
                print("\n[Error] El monto ingresado no es válido. Debe ser un número.")
                
        elif opcion == '2':
            print("\n--- REPORTE DE GASTOS ACUMULADOS ---")
            reporte = bd.generar_reporte_agrupado()
            
            if not reporte:
                print("Aún no tienes gastos registrados.")
            else:
                total_general = 0
                print(f"{'CATEGORÍA':<25} | {'TOTAL (S/.)':<10}")
                print("-" * 40)
                for fila in reporte:
                    categoria, total = fila
                    print(f"{categoria:<25} | S/. {total:.2f}")
                    total_general += total
                
                print("-" * 40)
                print(f"{'TOTAL GASTADO:':<25} | S/. {total_general:.2f}")
                
        elif opcion == '3':
            print("\nCerrando el asistente. ¡Hasta luego!")
            break
        else:
            print("\n[Error] Opción no válida. Intenta nuevamente.")

if __name__ == "__main__":
    main()