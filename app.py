# app.py


from flask import Flask, render_template
from app.routes_api import api
from app.routes_admin import admin
import os

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(admin, url_prefix="/api")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/comparativa")
def comparativa():
    return render_template("chat_openai.html")

@app.route("/admin")
def admin_panel():
    timestamp_path = "faiss_data/last_index.txt"
    if os.path.exists(timestamp_path):
        with open(timestamp_path) as f:
            ultima = f.read().strip()
    else:
        ultima = "Nunca se ha indexado."
    return render_template("admin.html", ultima_indexacion=ultima)

if __name__ == "__main__":
    app.run(debug=True)