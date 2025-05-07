# test_faiss.py

from app.utils.faiss_index import (
    indexar_contenido,
    guardar_indice,
    cargar_indice,
    buscar_similares,
    reset_indice,
    metadata
)

def test_indexar_y_buscar():
    print("🔄 Reiniciando índice...")
    reset_indice()

    textos = [
        "El Ayuntamiento de Onda ha abierto una nueva convocatoria de subvenciones.",
        "Las oficinas municipales estarán cerradas el próximo lunes por festivo.",
        "Se ha publicado el pliego para la licitación del servicio de limpieza viaria.",
        "La piscina municipal reabrirá sus puertas el 15 de junio con aforo limitado.",
        "Nuevo sistema de cita previa para atención ciudadana disponible desde el portal web."
    ]

    print("✅ Indexando 5 fragmentos...")
    indexar_contenido(textos, origen="https://www.onda.es/pruebas")

    print("💾 Guardando índice en disco...")
    guardar_indice()

    print("♻️ Cargando índice desde disco...")
    cargar_indice()

    print(f"📦 Total fragmentos tras carga: {len(metadata)}")

    consulta = "¿Cómo pedir cita previa en el ayuntamiento?"
    print(f"\n🔍 Consulta: {consulta}")
    resultados = buscar_similares(consulta, top_k=3)

    print("\n📌 Resultados más relevantes:")
    for i, r in enumerate(resultados, 1):
        print(f"{i}. {r['texto'][:120]}...")
        print(f"   ↪️ Origen: {r['origen']}\n")

if __name__ == "__main__":
    test_indexar_y_buscar()
