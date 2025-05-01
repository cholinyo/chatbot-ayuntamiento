# app/rag_engine.py

"""
Este módulo implementa la función consultar_rag(pregunta)
y la función ejecutar_indexacion_local() que indexa fuentes configuradas manualmente.
Cada fuente puede incluir '| tipo=sitemap | max_paginas=NUM' y los selectores se leen desde 'faiss_data/selectores.txt'
"""

import os
import logging
import time
from app.domain_crawler import obtener_urls_desde_sitemap, crawl_dominio
from app.ingestion import extraer_texto_web
from app.vector_indexing import indexar_fragmentos, buscar_fragmento_relevante
from app.index_storage import cargar_indice

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

# Cargar índice existente
cargar_indice()

# Leer selectores configurables desde archivo editable
ruta_selectores = "faiss_data/selectores.txt"
SELECTORES_AMPLIOS = ['p', 'h1', 'h2', 'h3', 'article', 'section', 'div']
if os.path.exists(ruta_selectores):
    with open(ruta_selectores, encoding="utf-8") as f:
        SELECTORES_AMPLIOS = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    logging.info(f"📌 Selectores personalizados cargados: {SELECTORES_AMPLIOS}")


def ejecutar_indexacion_local() -> int:
    """
    Ejecuta el proceso completo de extracción e indexación
    desde las fuentes almacenadas en faiss_data/fuentes.txt
    Cada línea puede incluir '| tipo=sitemap | max_paginas=NUM'
    """
    total_fragmentos = 0
    ruta_fuentes = "faiss_data/fuentes.txt"

    if not os.path.exists(ruta_fuentes):
        logging.warning("⚠️ No se encontró faiss_data/fuentes.txt. No se indexará nada.")
        return 0

    with open(ruta_fuentes, encoding="utf-8") as f:
        lineas = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for linea in lineas:
        partes = [p.strip() for p in linea.split("|") if p.strip()]
        url = partes[0]
        tipo = "pagina"
        max_paginas = 50

        for p in partes[1:]:
            if p.startswith("tipo="):
                tipo = p.replace("tipo=", "").strip()
            elif p.startswith("max_paginas="):
                try:
                    max_paginas = int(p.replace("max_paginas=", "").strip())
                except ValueError:
                    pass

        if tipo == "sitemap":
            urls = obtener_urls_desde_sitemap(url, dominio_filtrado=None, max_paginas=max_paginas)
            logging.info(f"🌐 Sitemap: {url} → {len(urls)} páginas detectadas")
        elif tipo == "dominio":
            urls = crawl_dominio(url, max_paginas=max_paginas)
            logging.info(f"🏛️ Dominio: {url} → {len(urls)} páginas detectadas")
        else:
            urls = [url]
            logging.info(f"📄 URL directa: {url}")

        for u in urls:
            fragmentos = extraer_texto_web(u, selectores=SELECTORES_AMPLIOS)
            count = indexar_fragmentos(fragmentos, u)
            total_fragmentos += count
            logging.info(f"✅ {count} fragmentos indexados desde: {u}")

    logging.info(f"📚 Total indexado en esta sesión: {total_fragmentos}")
    return total_fragmentos


def consultar_rag(pregunta: str) -> str:
    inicio = time.time()
    fragmento = buscar_fragmento_relevante(pregunta)
    duracion = time.time() - inicio
    logging.info(f"[RAG local] Pregunta: '{pregunta}' → Respuesta: '{fragmento[:100]}...' ({duracion:.2f}s)")
    return f"🤖 Según el contenido oficial: {fragmento}\n⏱️ Tiempo de respuesta: {duracion:.2f} segundos"
