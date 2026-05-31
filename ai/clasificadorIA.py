from transformers import pipeline

class ClasificadorIA:
    def __init__(self):
        print("\n[Sistema] Cargando modelo IA...")

        self.clasificador = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        )

        # Estas deben coincidir con tu tabla categories
        self.categorias_candidatas = [
            "Comida",
            "Transporte",
            "Educacion",
            "Entretenimiento",
            "Salud",
            "Hogar"
        ]

    def clasificar(self, descripcion):
        """Devuelve la categoría como texto"""
        resultado = self.clasificador(descripcion, self.categorias_candidatas)
        return resultado['labels'][0]

    def categorizar_y_mapear(self, descripcion, categorias_db):
        """
        Categoriza y devuelve el ID de categoría desde la BD
        
        categorias_db: lista de objetos Category()
        """

        categoria_texto = self.clasificar(descripcion)

        # Buscar en la BD (lista de objetos Category)
        for cat in categorias_db:
            if cat.description.lower() == categoria_texto.lower():
                return cat.id_category

        return None  # si no encuentra