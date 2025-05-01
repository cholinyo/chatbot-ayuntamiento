# app/openai_rag.py

"""
Este módulo permite combinar el sistema RAG local (con FAISS) con generación de texto
vía OpenAI, usando el nuevo cliente compatible con openai>=1.0.0.
El modelo puede cambiarse dinámicamente según una variable global elegida en el panel admin.
"""

import os
import logging
import numpy as np
import time
from openai import OpenAI
from app.vector_indexing import documentos_indexados, modelo, index
from app.index_storage import cargar_indice

# Configurar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Modelo usado (por defecto)
modelo_openai = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

# Cargar índice FAISS desde disco si está disponible
cargar_indice()

def establecer_modelo(nombre_modelo: str):
    global modelo_openai
    modelo_openai = nombre_modelo
    logging.info(f"🧠 Modelo OpenAI actualizado a: {modelo_openai}")

def obtener_modelo():
    return modelo_openai

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

def generar_respuesta_openai(pregunta: str, contexto: list[str]) -> tuple[str, float, str]:
    prompt = (
        "Usa la siguiente información para responder de forma clara y precisa.\n\n"
        "Contexto:\n" +
        "\n".join(f"- {frag}" for frag in contexto) +
        f"\n\nPregunta: {pregunta}\nRespuesta:"
    )

    try:
        inicio = time.time()
        respuesta = client.chat.completions.create(
            model=modelo_openai,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400
        )
        duracion = time.time() - inicio
        mensaje = respuesta.choices[0].message.content.strip()
        logging.info(f"[RAG+OpenAI] Modelo: {modelo_openai} | Pregunta: '{pregunta}' → Respuesta: '{mensaje[:100]}...' ({duracion:.2f}s)")
        return mensaje, duracion, modelo_openai

    except Exception as e:
        logging.error(f"❌ Error con OpenAI: {e}")
        return "⚠️ No se pudo generar una respuesta con el modelo de lenguaje.", 0, "error"

def consultar_rag_con_openai(pregunta: str) -> dict:
    contexto = obtener_top_k_fragmentos(pregunta, k=3)
    if not contexto:
        logging.warning(f"⚠️ Sin contexto disponible para: '{pregunta}'")
        return {
            "respuesta": "⚠️ No hay suficiente contexto disponible para responder.",
            "fragmentos": []
        }

    respuesta, duracion, modelo = generar_respuesta_openai(pregunta, contexto)
    return {
        "respuesta": f"{respuesta}\n⏱️ Tiempo de respuesta: {duracion:.2f} segundos\n🤖 Modelo: {modelo}",
        "fragmentos": contexto
    }
