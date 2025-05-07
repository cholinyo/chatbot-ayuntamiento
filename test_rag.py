# test_rag.py

from app.utils.faiss_index import (
    indexar_contenido,
    guardar_indice,
    cargar_indice,
    reset_indice,
    metadata
)
from app.rag_engine import consultar_rag

def test_chatbot_rag():
    print("🧽 Reiniciando índice FAISS...")
    reset_indice()

    textos = [
        "El Ayuntamiento de Onda ha lanzado una nueva convocatoria de subvenciones culturales para asociaciones locales.",
        "La atención ciudadana requiere cita previa a través del portal web del Ayuntamiento.",
        "La zona azul de aparcamiento será gratuita durante todo el mes de agosto.",
        "La biblioteca municipal amplía su horario hasta las 22h durante los exámenes.",
        "El servicio de limpieza viaria incluye también la desinfección semanal de los parques infantiles."
    ]

    print("📥 Indexando fragmentos de ejemplo...")
    indexar_contenido(textos, origen="https://www.onda.es/test")

    print("💾 Guardando índice...")
    guardar_indice()

    print("♻️ Cargando índice...")
    cargar_indice()

    print(f"📊 Total fragmentos cargados: {len(metadata)}")

    preguntas = [
        "¿Dónde puedo pedir cita previa para atención ciudadana?",
        "¿Es gratis aparcar en agosto?",
        "¿Cómo conseguir una subvención cultural?",
        "¿A qué hora cierra la biblioteca?",
        "¿Limpian los parques infantiles?"
    ]

    print("\n🧠 Probando respuestas del chatbot:\n")
    for pregunta in preguntas:
        print(f"🗨️ Usuario: {pregunta}")
        respuesta = consultar_rag(pregunta)
        print(f"{respuesta}\n")

if __name__ == "__main__":
    test_chatbot_rag()
