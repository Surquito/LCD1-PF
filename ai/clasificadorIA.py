from transformers import pipeline
import re

class ClasificadorIA:
    def __init__(self):
        print("\n[Sistema] Cargando modelo IA...")
        self.clasificador = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        )
        self.categorias_candidatas = [
            "Comida",
            "Transporte",
            "Educacion",
            "Entretenimiento",
            "Salud",
            "Hogar"
        ]
        #se arego esta seccion para poder clasificar por palabras clave y no depender tanto del modelo de IA, ya que a veces falla con ciertas descripciones
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

    def clasificar(self, descripcion):
        """Devuelve la categoría como texto"""
        if self._es_educacion_por_keywords(descripcion):
            return "Educacion"
        resultado = self.clasificador(descripcion, self.categorias_candidatas)
        return resultado['labels'][0]

    def categorizar_y_mapear(self, descripcion, categorias_db):
        """
        Categoriza y devuelve el ID de categoría desde la BD
        categorias_db: lista de objetos Category()
        """
        categoria_texto = self.clasificar(descripcion)

        # Buscar en la BD
        for cat in categorias_db:
            if cat.description.lower() == categoria_texto.lower():
                return cat.id_category

        return None