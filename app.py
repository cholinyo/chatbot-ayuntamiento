# app.py

import logging
from flask import Flask, render_template, request, jsonify
from app.rag_engine import consultar_rag
from app.vector_indexing import listar_urls_indexadas

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pregunta = data.get("pregunta")
    if not pregunta:
        logging.warning("Petición sin pregunta recibida")
        return jsonify({"error": "Falta la pregunta"}), 400
    try:
        respuesta = consultar_rag(pregunta)
        logging.info(f"Consulta: '{pregunta}' → Respuesta: '{respuesta[:100]}...'")
        return jsonify({"respuesta": respuesta})
    except Exception as e:
        logging.error(f"Error durante la consulta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/api/indexadas', methods=['GET'])
def indexadas():
    urls = list(listar_urls_indexadas())
    logging.info(f"Consulta de URLs indexadas: {len(urls)} encontradas")
    return jsonify({"urls": urls})

if __name__ == "__main__":
    app.run(debug=True)

