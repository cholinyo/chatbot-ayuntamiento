# app/index_storage.py

"""
Este módulo gestiona el almacenamiento y recuperación del índice FAISS,
además del contexto asociado (fragmentos y origen) desde disco.
"""

import os
import pickle
import faiss
from app.vector_indexing import index, documentos_indexados, origen_fragmentos

DIRECTORIO_INDEXADO = "faiss_data"
RUTA_INDEX = os.path.join(DIRECTORIO_INDEXADO, "index.faiss")
RUTA_FRAGMENTOS = os.path.join(DIRECTORIO_INDEXADO, "fragmentos.pkl")
RUTA_ORIGENES = os.path.join(DIRECTORIO_INDEXADO, "origenes.pkl")


def guardar_indice():
    """Guarda el índice FAISS y los fragmentos en disco."""
    if not os.path.exists(DIRECTORIO_INDEXADO):
        os.makedirs(DIRECTORIO_INDEXADO)

    faiss.write_index(index, RUTA_INDEX)

    with open(RUTA_FRAGMENTOS, "wb") as f:
        pickle.dump(documentos_indexados, f)

    with open(RUTA_ORIGENES, "wb") as f:
        pickle.dump(origen_fragmentos, f)

    print("📦 Índice FAISS y contexto guardados correctamente.")


def cargar_indice():
    """Carga el índice FAISS y los fragmentos desde disco, si existen."""
    global index, documentos_indexados, origen_fragmentos

    if not os.path.exists(RUTA_INDEX):
        print("⚠️ No se encontró índice FAISS guardado. Se usará uno vacío.")
        return

    index = faiss.read_index(RUTA_INDEX)

    with open(RUTA_FRAGMENTOS, "rb") as f:
        documentos_indexados.clear()
        documentos_indexados.extend(pickle.load(f))

    with open(RUTA_ORIGENES, "rb") as f:
        origen_fragmentos.clear()
        origen_fragmentos.update(pickle.load(f))

    print(f"✅ Índice FAISS cargado: {len(documentos_indexados)} fragmentos disponibles.")
