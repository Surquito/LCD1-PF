from transformers import pipeline
import re

class ClasificadorIA:
    def __init__(self):
        print("\n[Sistema] Cargando modelo IA...")
        self.clasificador = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        )
        # Palabras clave para detectar educación
        self.keywords_educacion = [
            "cibertec", "senati", "sencico", "tecsup", "idat", "iest", "cetpro",
            "pucp", "upc", "upn", "utp", "usil", "ucsur", "ucv", "unmsm",
            "universidad", "instituto", "colegio", "escuela", "academia",
            "facultad", "diplomado", "maestria", "posgrado",
            "matricula", "mensualidad", "pension escolar", "pension universitaria",
            "certamen", "examen de admision", "tutoria",
            "curso", "taller educativo", "capacitacion",
        ]

    def _es_educacion_por_keywords(self, descripcion: str) -> bool:
        texto = descripcion.lower()
        texto = texto.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        for kw in self.keywords_educacion:
            kw_norm = kw.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            if re.search(r'\b' + re.escape(kw_norm) + r'\b', texto):
                return True
        return False

    def clasificar_con_candidatas(self, descripcion, candidatas):
        """Clasifica la descripción entre una lista dinámica de candidatas, devolviendo (etiqueta, score)"""
        if not candidatas:
            return None, 0.0
        resultado = self.clasificador(descripcion, candidatas)
        return resultado['labels'][0], resultado['scores'][0]

    def categorizar_y_mapear(self, descripcion, type_txn='gasto'):
        """
        Categoriza y devuelve (id_category, description) desde la BD.
        Si la confianza es menor a 0.35, se asigna a la categoría comodín ('Otros Gastos' u 'Otros Ingresos').
        """
        from services.category_service import get_all_categories
        categorias_db = get_all_categories()

        # Filtrar solo categorías principales del tipo correcto (id_subcategory es None/Null)
        categorias_principales = [
            c for c in categorias_db 
            if c.id_subcategory is None and c.type_category == type_txn
        ]
        
        # Verificar palabras clave de educación primero
        if type_txn == 'gasto' and self._es_educacion_por_keywords(descripcion):
            categoria_educacion = next((c for c in categorias_principales if c.description.lower() == 'educacion'), None)
            if categoria_educacion:
                return categoria_educacion.id_category, categoria_educacion.description
        
        # Buscar si existe la categoría comodín correspondiente
        nombre_otros = 'otros ingresos' if type_txn == 'ingreso' else 'otros gastos'
        categoria_otros = next((c for c in categorias_principales if c.description.lower() == nombre_otros), None)
        
        # Candidatas específicas para evaluar con la IA (excluyendo la comodín)
        categorias_especificas = [c for c in categorias_principales if c.description.lower() != nombre_otros]
        candidatas_nombres = [c.description for c in categorias_especificas]

        # Si no hay categorías principales, retornar la de Otros si existe
        if not candidatas_nombres:
            if categoria_otros:
                return categoria_otros.id_category, categoria_otros.description
            return None, "Desconocida"

        categoria_texto, score = self.clasificar_con_candidatas(descripcion, candidatas_nombres)

        # Si la confianza es baja (menor a 0.35), clasificar como la comodín correspondiente
        if score < 0.35 and categoria_otros:
            print(f"-> [IA] Confianza baja ({score:.2f}) para '{descripcion}'. Asignado automáticamente a '{categoria_otros.description}'.")
            return categoria_otros.id_category, categoria_otros.description

        # Buscar en la BD la categoría ganadora
        for cat in categorias_especificas:
            if cat.description.lower() == categoria_texto.lower():
                return cat.id_category, cat.description

        if categoria_otros:
            return categoria_otros.id_category, categoria_otros.description
        return None, "Desconocida"  # si no encuentra

    def categorizar_y_mapear_subcategoria(self, descripcion, subcategorias_db):
        """
        Categoriza y devuelve (id_subcategory, description) desde la BD
        
        subcategorias_db: lista de objetos Category() que son subcategorías
        """
        if not subcategorias_db:
            return None, "Sin subcategoría"
            
        candidatas = [s.description for s in subcategorias_db]
        subcat_texto, score = self.clasificar_con_candidatas(descripcion, candidatas)
        
        for sub in subcategorias_db:
            if sub.description.lower() == subcat_texto.lower():
                return sub.id_category, sub.description
                
        return None, "Sin subcategoría"
