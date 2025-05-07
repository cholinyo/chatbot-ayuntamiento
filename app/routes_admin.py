# app/routes_admin.py

from flask import Blueprint, jsonify, request, render_template
from app.rag_engine import ejecutar_indexacion_local
from app.utils.faiss_index import guardar_indice, metadata
from app.openai_rag import establecer_modelo
from app.domain_crawler import obtener_urls_desde_sitemap
from datetime import datetime
import os

admin = Blueprint("admin", __name__)

@admin.route("/reindexar", methods=["POST"])
def reindexar():
    total = ejecutar_indexacion_local()
    guardar_indice()

    # Guardar timestamp
    ruta = "faiss_data/last_index.txt"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(fecha)

    return jsonify({
        "status": "ok",
        "mensaje": f"✅ Se indexaron {total} fragmentos y se guardó el índice. ({fecha})"
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
    # Cargar textos guardados
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

    # Estadísticas
    total_fragmentos = len(metadata)
    urls = [m["origen"] for m in metadata]
    total_urls = len(set(urls))
    total_urls_sitemap = sum(1 for u in urls if "sitemap" in u.lower())
    total_urls_directas = sum(1 for u in urls if "id_boto=" in u or "index.php" in u)

    return render_template("admin.html",
        ultima_indexacion=ultima,
        fuentes_cargadas=fuentes,
        selectores_cargados=selectores,
        total_urls=total_urls,
        total_fragmentos=total_fragmentos,
        total_urls_sitemap=total_urls_sitemap,
        total_urls_directas=total_urls_directas
    )
