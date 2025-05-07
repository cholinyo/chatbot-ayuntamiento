# app.py

from flask import Flask, render_template
from app.routes_api import api as api_bp
from app.routes_admin import admin as admin_bp
from app.utils.faiss_index import cargar_indice
import os

app = Flask(__name__)

# Cargar el índice FAISS al iniciar
cargar_indice()

# Registrar Blueprints
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(admin_bp)  # admin ya gestiona /admin internamente

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/comparativa")
def comparativa():
    return render_template("chat_openai.html")

@app.route("/admin")
def admin_panel():
    timestamp_path = "faiss_data/last_index.txt"
    fuentes_path = "fuentes.txt"
    selectores_path = "selectores.txt"

    if os.path.exists(timestamp_path):
        with open(timestamp_path) as f:
            ultima = f.read().strip()
    else:
        ultima = "Nunca se ha indexado."

    if os.path.exists(fuentes_path):
        with open(fuentes_path, encoding="utf-8") as f:
            fuentes = f.read().strip()
    else:
        fuentes = ""

    if os.path.exists(selectores_path):
        with open(selectores_path, encoding="utf-8") as f:
            selectores = f.read().strip()
    else:
        selectores = ""

    # Leer estadísticas simuladas
    from app.utils.faiss_index import metadata
    total_fragmentos = len(metadata)
    urls_unicas = list(set(m["origen"] for m in metadata))
    total_urls = len(urls_unicas)
    total_urls_sitemap = len([u for u in urls_unicas if "sitemap" in u])
    total_urls_directas = len([u for u in urls_unicas if "id_boto=" in u or "index.php" in u])

    return render_template("admin.html",
                           ultima_indexacion=ultima,
                           fuentes_cargadas=fuentes,
                           selectores_cargados=selectores,
                           total_fragmentos=total_fragmentos,
                           total_urls=total_urls,
                           total_urls_sitemap=total_urls_sitemap,
                           total_urls_directas=total_urls_directas)

if __name__ == "__main__":
    app.run(debug=True)
