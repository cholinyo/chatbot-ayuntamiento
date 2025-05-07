# app/utils/faiss_index.py

import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Inicializar modelo
modelo_embeddings = SentenceTransformer("all-MiniLM-L6-v2")  # Puedes cambiar por otro modelo

# Ruta del índice
RUTA_INDICE = "faiss_data/faiss.index"
RUTA_METADATA = "faiss_data/metadata.pkl"

# Estructura del índice
dim = 384  # Dimensión del modelo 'all-MiniLM-L6-v2'
index = faiss.IndexFlatL2(dim)
metadata: List[Dict] = []  # Exportado como global

def indexar_contenido(fragmentos: List[str], origen: str):
    global index, metadata
    embeddings = modelo_embeddings.encode(fragmentos, convert_to_numpy=True)
    index.add(embeddings)
    metadata.extend([{"texto": frag, "origen": origen} for frag in fragmentos])

def guardar_indice():
    global index, metadata
    os.makedirs("faiss_data", exist_ok=True)
    faiss.write_index(index, RUTA_INDICE)
    with open(RUTA_METADATA, "wb") as f:
        pickle.dump(metadata, f)

def cargar_indice():
    global index, metadata
    if os.path.exists(RUTA_INDICE):
        index = faiss.read_index(RUTA_INDICE)
    else:
        index = faiss.IndexFlatL2(dim)

    if os.path.exists(RUTA_METADATA):
        with open(RUTA_METADATA, "rb") as f:
            metadata = pickle.load(f)
    else:
        metadata = []

def buscar_similares(query: str, top_k: int = 5):
    global index, metadata
    embedding = modelo_embeddings.encode([query], convert_to_numpy=True)
    D, I = index.search(embedding, top_k)
    resultados = []
    for i in I[0]:
        if i < len(metadata):
            resultados.append(metadata[i])
    return resultados

def reset_indice():
    """Útil para tests o reindexaciones limpias"""
    global index, metadata
    index = faiss.IndexFlatL2(dim)
    metadata = []
