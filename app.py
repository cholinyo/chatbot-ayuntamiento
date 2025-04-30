# app.py
from flask import Flask, render_template, request, jsonify
from app.rag_engine import consultar_rag

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pregunta = data.get("pregunta")
    if not pregunta:
        return jsonify({"error": "Falta la pregunta"}), 400
    respuesta = consultar_rag(pregunta)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
