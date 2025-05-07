# app/rag_engine.py

import os
import logging
import sys
import time
from app.utils.faiss_index import indexar_contenido, buscar_similares, cargar_indice, metadata
from app.domain_crawler import obtener_urls_desde_sitemap, crawl_dominio
from app.ingestion import extraer_texto_web

# Configuración de logging con soporte para emojis
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

# Cargar índice FAISS al iniciar
cargar_indice()

# Cargar selectores desde archivo (editable)
ruta_selectores = "faiss_data/selectores.txt"
SELECTORES_AMPLIOS = ['p', 'h1', 'h2', 'h3', 'article', 'section', 'div']
if os.path.exists(ruta_selectores):
    with open(ruta_selectores, encoding="utf-8") as f:
        SELECTORES_AMPLIOS = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    logging.info(f"📌 Selectores personalizados cargados: {SELECTORES_AMPLIOS}")

def ejecutar_indexacion_local() -> int:
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
                tipo = p.split("=")[1].strip()
            elif p.startswith("max_paginas="):
                try:
                    max_paginas = int(p.split("=")[1].strip())
                except ValueError:
                    pass

        # Resolver las URLs a procesar
        if tipo == "sitemap":
            urls = obtener_urls_desde_sitemap(url, dominio_filtrado=None, max_paginas=max_paginas)
            logging.info(f"🌐 Sitemap: {url} → {len(urls)} páginas detectadas")
        elif tipo == "dominio":
            urls = crawl_dominio(url, max_paginas=max_paginas)
            logging.info(f"🏛️ Dominio: {url} → {len(urls)} páginas detectadas")
        else:
            urls = [url]
            logging.info(f"📄 URL directa: {url}")

        # Extraer e indexar
        for u in urls:
            fragmentos = extraer_texto_web(u, selectores=SELECTORES_AMPLIOS)
            if fragmentos:
                indexar_contenido(fragmentos, origen=u)
                total_fragmentos += len(fragmentos)
                logging.info(f"✅ {len(fragmentos)} fragmentos indexados desde: {u}")
            else:
                logging.info(f"⚠️ 0 fragmentos desde: {u}")

    logging.info(f"📚 Total indexado en esta sesión: {total_fragmentos}")
    return total_fragmentos


def consultar_rag(pregunta: str) -> str:
    inicio = time.time()
    resultados = buscar_similares(pregunta, top_k=1)
    duracion = time.time() - inicio

    if not resultados:
        return "🤖 Lo siento, no encontré información relacionada."

    fragmento = resultados[0]['texto']
    return f"🤖 Según el contenido oficial:\n{fragmento}\n⏱️ Tiempo de respuesta: {duracion:.2f} segundos"
