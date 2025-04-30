# app/rag_engine.py

"""
Este módulo implementa la función consultar_rag(pregunta), que combina:
- extracción de URLs desde el sitemap del Ayuntamiento
- extracción de texto desde múltiples páginas
- vectorización con sentence-transformers
- búsqueda semántica con FAISS

Es la lógica de recuperación y respuesta principal del chatbot.
"""

import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from app.domain_crawler import obtener_urls_desde_sitemap
from app.ingestion import extraer_texto_web
from app.vector_indexing import indexar_fragmentos, buscar_fragmento_relevante

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

# Obtener dominio y sitemap
DOMINIO_INICIAL = os.getenv("DOMINIO_AYUNTAMIENTO", "https://www.ayuntamiento.es")
SITEMAP_URL = f"{DOMINIO_INICIAL.rstrip('/')}/sitemap.xml"
DOMINIO_BASE = urlparse(DOMINIO_INICIAL).netloc

# Paso 1: obtener URLs del sitemap del dominio
URLS_MUNICIPALES = obtener_urls_desde_sitemap(SITEMAP_URL, dominio_filtrado=DOMINIO_BASE, max_paginas=20)

# Paso 2: cargar y vectorizar todas las páginas web encontradas
SELECTORES_AMPLIOS = ['p', 'h1', 'h2', 'h3', 'article', 'section', 'div']

for url in URLS_MUNICIPALES:
    fragmentos = extraer_texto_web(url, selectores=SELECTORES_AMPLIOS)
    count = indexar_fragmentos(fragmentos, url)
    print(f"✅ {count} fragmentos indexados desde: {url}")

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
