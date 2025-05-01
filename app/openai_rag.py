# app/openai_rag.py

"""
Este módulo permite combinar el sistema RAG local (con FAISS) con generación de texto
vía OpenAI, usando los fragmentos recuperados como contexto. Integra logging detallado.
"""

import os
import logging
import openai
import numpy as np
import time
from app.vector_indexing import documentos_indexados, modelo, index

# Configurar la clave de API de OpenAI desde variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

def obtener_top_k_fragmentos(pregunta: str, k: int = 3) -> list:
    if not documentos_indexados:
        return []

    pregunta_embedding = modelo.encode([pregunta])
    _, indices = index.search(np.array(pregunta_embedding), k)

    fragmentos = []
    for idx in indices[0]:
        if idx < len(documentos_indexados):
            fragmentos.append(documentos_indexados[idx])

    logging.info(f"🔍 OpenAI RAG recuperó {len(fragmentos)} fragmentos para la pregunta: '{pregunta}'")
    return fragmentos

def generar_respuesta_openai(pregunta: str, contexto: list[str]) -> str:
    prompt = (
        "Usa la siguiente información para responder de forma clara y precisa.\n\n"
        "Contexto:\n" +
        "\n".join(f"- {frag}" for frag in contexto) +
        f"\n\nPregunta: {pregunta}\nRespuesta:"
    )

    try:
        inicio = time.time()
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400
        )
        duracion = time.time() - inicio
        mensaje = respuesta.choices[0].message.content.strip()
        logging.info(f"[RAG+OpenAI] Pregunta: '{pregunta}' → Respuesta: '{mensaje[:100]}...' ({duracion:.2f}s)")
        return mensaje, duracion

    except Exception as e:
        logging.error(f"❌ Error con OpenAI: {e}")
        return "⚠️ No se pudo generar una respuesta con el modelo de lenguaje.", 0

def consultar_rag_con_openai(pregunta: str) -> dict:
    contexto = obtener_top_k_fragmentos(pregunta, k=3)
    if not contexto:
        logging.warning(f"⚠️ Sin contexto disponible para: '{pregunta}'")
        return {
            "respuesta": "⚠️ No hay suficiente contexto disponible para responder.",
            "fragmentos": []
        }

    respuesta, duracion = generar_respuesta_openai(pregunta, contexto)
    return {
        "respuesta": f"{respuesta}\n⏱️ Tiempo de respuesta: {duracion:.2f} segundos",
        "fragmentos": contexto
    }
