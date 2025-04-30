"""
Este módulo implementa la función consultar_rag(pregunta), que combina:
- extracción de texto desde webs municipales
- vectorización con sentence-transformers
- búsqueda semántica con FAISS

Es la lógica de recuperación y respuesta principal del chatbot.
"""

from app.ingestion import extraer_texto_web
from app.vector_indexing import indexar_fragmentos, buscar_fragmento_relevante

# URL de ejemplo que será cargada al iniciar el bot
URL_MUNICIPAL = "https://www.ayuntamiento.es/tu-pagina"

# Paso inicial: cargar y vectorizar la web al iniciar
fragmentos_web = extraer_texto_web(URL_MUNICIPAL)
indexar_fragmentos(fragmentos_web)

def consultar_rag(pregunta: str) -> str:
    """
    Busca el fragmento más relevante para la pregunta
    y lo devuelve como respuesta contextualizada.

    Parámetros:
        pregunta (str): pregunta del ciudadano

    Retorna:
        str: respuesta generada basada en el contenido indexado
    """
    fragmento = buscar_fragmento_relevante(pregunta)
    return f"🤖 Según el contenido oficial: {fragmento}"
