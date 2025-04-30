# app/vector_indexing.py

"""
Este módulo permite vectorizar una lista de fragmentos de texto
usando `sentence-transformers` y almacenarlos en un índice FAISS.
"""

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Cargamos el modelo de embeddings local
modelo = SentenceTransformer("all-MiniLM-L6-v2")

# Inicializamos el índice FAISS con la dimensión del modelo (384 en este caso)
DIMENSION = 384
index = faiss.IndexFlatL2(DIMENSION)

# Lista para almacenar los fragmentos cargados (para trazabilidad)
documentos_indexados = []

def indexar_fragmentos(fragmentos: list):
    """
    Vectoriza e indexa los fragmentos recibidos con FAISS.

    Parámetros:
        fragmentos (list): lista de textos limpios a indexar

    Retorna:
        int: número de fragmentos añadidos al índice
    """
    if not fragmentos:
        return 0

    embeddings = modelo.encode(fragmentos)
    index.add(np.array(embeddings))
    documentos_indexados.extend(fragmentos)

    return len(fragmentos)

def buscar_fragmento_relevante(pregunta: str, k: int = 1) -> str:
    """
    Busca el fragmento más relevante para una pregunta.

    Parámetros:
        pregunta (str): texto introducido por el usuario
        k (int): número de resultados a devolver

    Retorna:
        str: texto del fragmento más cercano (top-1)
    """
    pregunta_embedding = modelo.encode([pregunta])
    _, indices = index.search(np.array(pregunta_embedding), k)

    if indices[0][0] < len(documentos_indexados):
        return documentos_indexados[indices[0][0]]
    else:
        return "No se encontró información relevante."

# Uso sugerido desde otro módulo:
# from ingestion import extraer_texto_web
# from vector_indexing import indexar_fragmentos, buscar_fragmento_relevante
# fragmentos = extraer_texto_web("https://ayuntamiento.es/tramites")
# indexar_fragmentos(fragmentos)
# print(buscar_fragmento_relevante("¿Cuáles son los requisitos para empadronarse?"))
