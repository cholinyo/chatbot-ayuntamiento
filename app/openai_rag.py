# NUEVA API compatible con openai>=1.0.0
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
from app.utils.faiss_index import buscar_similares

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo_actual = "gpt-4"

def establecer_modelo(nombre: str):
    global modelo_actual
    modelo_actual = nombre

def consultar_openai_rag(pregunta: str, top_k: int = 3) -> dict:
    fragmentos = buscar_similares(pregunta, top_k)
    contexto = "\n\n".join([f"- {f['texto']}" for f in fragmentos])
    prompt = f"""Eres un asistente del Ayuntamiento. Responde de forma clara y directa usando solo la información siguiente:

{contexto}

Pregunta: {pregunta}
Respuesta:"""

    try:
        response = client.chat.completions.create(
            model=modelo_actual,
            messages=[
                {"role": "system", "content": "Eres un asistente del Ayuntamiento que responde solo con la información proporcionada."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return {
            "respuesta": response.choices[0].message.content.strip(),
            "fragmentos": [f["texto"] for f in fragmentos]
        }
    except Exception as e:
        print("❌ Error en OpenAI:", e)
        return {
            "respuesta": f"❌ Error al contactar con OpenAI: {e}",
            "fragmentos": []
        }
