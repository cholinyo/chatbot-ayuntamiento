# app/routes_admin.py

from flask import Blueprint, jsonify, request
from app.rag_engine import ejecutar_indexacion_local
from app.index_storage import guardar_indice
from app.openai_rag import establecer_modelo
from datetime import datetime
import os

admin = Blueprint("admin", __name__)

@admin.route("/reindexar", methods=["POST"])
def reindexar():
    total = ejecutar_indexacion_local()
    guardar_indice()

    ruta = "faiss_data/last_index.txt"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w") as f:
        f.write(fecha)

    return jsonify({
        "status": "ok",
        "mensaje": f"Se indexaron {total} fragmentos y se guardó el índice. ({fecha})"
    })

@admin.route("/modelo", methods=["POST"])
def cambiar_modelo():
    data = request.get_json()
    modelo = data.get("modelo")
    if not modelo:
        return jsonify({"mensaje": "⚠️ No se especificó modelo."}), 400
    establecer_modelo(modelo)
    return jsonify({"mensaje": f"✅ Modelo actualizado a {modelo}"})

@admin.route("/fuentes", methods=["POST"])
def guardar_fuentes():
    data = request.get_json()
    texto = data.get("fuentes", "")
    os.makedirs("faiss_data", exist_ok=True)
    with open("faiss_data/fuentes.txt", "w", encoding="utf-8") as f:
        f.write(texto.strip())
    return jsonify({"mensaje": "✅ Fuentes guardadas correctamente."})

@admin.route("/selectores", methods=["POST"])
def guardar_selectores():
    data = request.get_json()
    texto = data.get("selectores", "")
    os.makedirs("faiss_data", exist_ok=True)
    with open("faiss_data/selectores.txt", "w", encoding="utf-8") as f:
        f.write(texto.strip())
    return jsonify({"mensaje": "✅ Selectores guardados correctamente."})

@admin.route("/admin")
def admin_panel():
    timestamp_path = "faiss_data/last_index.txt"
    fuentes_path = "faiss_data/fuentes.txt"
    selectores_path = "faiss_data/selectores.txt"

    ultima = "Nunca se ha indexado."
    if os.path.exists(timestamp_path):
        with open(timestamp_path) as f:
            ultima = f.read().strip()

    fuentes = ""
    if os.path.exists(fuentes_path):
        with open(fuentes_path, encoding="utf-8") as f:
            fuentes = f.read()

    selectores = ""
    if os.path.exists(selectores_path):
        with open(selectores_path, encoding="utf-8") as f:
            selectores = f.read()

    total_urls = 0
    total_fragmentos = 0
    try:
        from app.vector_indexing import documentos_indexados, origen_fragmentos
        total_fragmentos = len(documentos_indexados)
        total_urls = len(set(origen_fragmentos.values()))
    except Exception as e:
        print("[admin] Error contando estadísticas:", e)

    total_urls_sitemap = 0
    total_urls_directas = 0
    try:
        from app.domain_crawler import obtener_urls_desde_sitemap
        for line in fuentes.splitlines():
            if "#" in line or not line.strip():
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            url = parts[0]
            tipo = "pagina"
            maxp = 50
            for p in parts[1:]:
                if p.startswith("tipo="):
                    tipo = p.split("=")[1].strip()
                if p.startswith("max_paginas="):
                    try:
                        maxp = int(p.split("=")[1])
                    except: pass
            if tipo == "sitemap":
                try:
                    urls = obtener_urls_desde_sitemap(url, dominio_filtrado=None, max_paginas=maxp)
                    total_urls_sitemap += len(urls)
                except: pass
            elif tipo == "pagina":
                total_urls_directas += 1
    except Exception as e:
        print("[admin] Error contando URLs:", e)

    from flask import render_template
    return render_template("admin.html",
        ultima_indexacion=ultima,
        fuentes_cargadas=fuentes,
        selectores_cargados=selectores,
        total_urls=total_urls,
        total_fragmentos=total_fragmentos,
        total_urls_sitemap=total_urls_sitemap,
        total_urls_directas=total_urls_directas
    )
