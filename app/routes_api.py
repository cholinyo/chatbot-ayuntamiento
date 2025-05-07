# app/routes_api.py

from flask import Blueprint, jsonify, request
from app.ingestion import extraer_texto_web
from app.domain_crawler import crawl_dominio, obtener_urls_desde_sitemap
from app.utils.faiss_index import indexar_contenido, guardar_indice, cargar_indice
from app.rag_engine import consultar_rag
import os

api = Blueprint("api", __name__)

@api.route("/reindexar", methods=["POST"])
def reindexar():
    total_fragmentos = 0
    urls_procesadas = []

    # Leer selectores
    selectores_path = "faiss_data/selectores.txt"
    selectores = []
    if os.path.exists(selectores_path):
        with open(selectores_path, "r", encoding="utf-8") as f:
            selectores = f.read().split(",")
            selectores = [s.strip() for s in selectores if s.strip()]
    if not selectores:
        selectores = ["p", "h1", "h2", "div"]

    # Leer fuentes
    fuentes_path = "faiss_data/fuentes.txt"
    fuentes = []
    if os.path.exists(fuentes_path):
        with open(fuentes_path, "r", encoding="utf-8") as f:
            fuentes = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for linea in fuentes:
        partes = linea.split("|")
        url = partes[0].strip()
        tipo = "pagina"
        max_paginas = 50

        for parte in partes[1:]:
            if "tipo=" in parte:
                tipo = parte.split("=")[1].strip()
            elif "max_paginas=" in parte:
                try:
                    max_paginas = int(parte.split("=")[1].strip())
                except ValueError:
                    pass

        # Obtener URLs
        if tipo == "dominio":
            urls = crawl_dominio(url, max_paginas=max_paginas)
        elif tipo == "sitemap":
            urls = obtener_urls_desde_sitemap(url, max_paginas=max_paginas)
        else:
            urls = [url]

        print(f"🌐 URLs descubiertas: {urls}")
        urls_procesadas.extend(urls)

        for u in urls:
            fragmentos = extraer_texto_web(u, selectores)
            if fragmentos:
                indexar_contenido(fragmentos, origen=u)
                total_fragmentos += len(fragmentos)
            print(f"✅ {len(fragmentos)} fragmentos indexados desde: {u}")

    guardar_indice()
    mensaje = f"📚 Total indexado en esta sesión: {total_fragmentos} fragmentos desde {len(urls_procesadas)} URLs"
    print(mensaje)
    return jsonify({"mensaje": mensaje})

@api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pregunta = data.get("pregunta", "").strip()

    if not pregunta:
        return jsonify({"respuesta": "⚠️ No se proporcionó ninguna pregunta."}), 400

    print(f"🗨️ Pregunta recibida: {pregunta}")  # ← Registro en consola

    respuesta = consultar_rag(pregunta)
    print(f"🤖 Respuesta generada: {respuesta[:100]}...\n")  # ← Resumen en consola

    return jsonify({"respuesta": respuesta})

from app.openai_rag import consultar_openai_rag

@api.route("/chat_openai", methods=["POST"])
def chat_openai():
    data = request.get_json()
    pregunta = data.get("pregunta", "").strip()

    if not pregunta:
        return jsonify({"respuesta": "⚠️ No se proporcionó ninguna pregunta."}), 400

    print(f"✨ [OPENAI] Pregunta recibida: {pregunta}")
    resultado = consultar_openai_rag(pregunta)
    return jsonify(resultado)
