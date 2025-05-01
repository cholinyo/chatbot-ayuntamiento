# app/routes_api.py

from flask import Blueprint, request, jsonify
from app.rag_engine import consultar_rag
from app.openai_rag import consultar_rag_con_openai

api = Blueprint("api", __name__)

@api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pregunta = data.get("pregunta", "")
    if not pregunta:
        return jsonify({"error": "No se recibió pregunta."}), 400
    respuesta = consultar_rag(pregunta)
    return jsonify({"respuesta": respuesta})

@api.route("/chat_openai", methods=["POST"])
def chat_openai():
    data = request.get_json()
    pregunta = data.get("pregunta", "")
    if not pregunta:
        return jsonify({"error": "No se recibió pregunta."}), 400
    resultado = consultar_rag_con_openai(pregunta)
    return jsonify(resultado)
