# app/vector_indexing.py

"""
Este módulo permite vectorizar una lista de fragmentos de texto
usando `sentence-transformers` y almacenarlos en un índice FAISS.
También expone una función para consultar las URLs desde las que
se ha obtenido contenido indexado.
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
documentos_indexados = []         # Lista de texto
origen_fragmentos = {}            # Diccionario: fragmento -> URL de origen

def indexar_fragmentos(fragmentos: list, url: str = None):
    """
    Vectoriza e indexa los fragmentos recibidos con FAISS.

    Parámetros:
        fragmentos (list): lista de textos limpios a indexar
        url (str): URL de donde se extrajeron los fragmentos (opcional)

    Retorna:
        int: número de fragmentos añadidos al índice
    """
    if not fragmentos:
        return 0

    embeddings = modelo.encode(fragmentos)
    index.add(np.array(embeddings))

    for i, texto in enumerate(fragmentos):
        documentos_indexados.append(texto)
        if url:
            origen_fragmentos[texto] = url

    return len(fragmentos)

def buscar_fragmento_relevante(pregunta: str, k: int = 1) -> str:
    """
    Busca el fragmento más relevante para una pregunta.

    Parámetros:
        pregunta (str): texto introducido por el usuario
        k (int): número de resultados a devolver

    Retorna:
        str: texto del fragmento más cercano (top-1) o un mensaje si no hay datos
    """
    if len(documentos_indexados) == 0:
        return "⚠️ No hay contenido indexado. Por favor, revisa las URLs cargadas."

    pregunta_embedding = modelo.encode([pregunta])
    _, indices = index.search(np.array(pregunta_embedding), k)

    if indices[0][0] < len(documentos_indexados):
        return documentos_indexados[indices[0][0]]
    else:
        return "⚠️ No se encontraron resultados relevantes en la base de conocimiento."

def listar_urls_indexadas() -> set:
    """
    Devuelve el conjunto único de URLs desde las que se han indexado fragmentos.
    """
    return set(origen_fragmentos.values())
