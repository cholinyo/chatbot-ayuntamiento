
# scripts/diagnostico_indexacion.py

import os
from app.domain_crawler import obtener_urls_desde_sitemap, crawl_dominio
from app.ingestion import extraer_texto_web
from app.utils.faiss_index import metadata, cargar_indice

def cargar_fuentes():
    path = "faiss_data/fuentes.txt"
    if not os.path.exists(path):
        print("❌ No se encontró faiss_data/fuentes.txt")
        return []
    with open(path, encoding="utf-8") as f:
        lineas = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return lineas

def cargar_selectores():
    path = "faiss_data/selectores.txt"
    if not os.path.exists(path):
        return ["p", "h1", "h2", "h3", "div"]
    with open(path, encoding="utf-8") as f:
        return [s.strip() for s in f.read().split(",") if s.strip()]

def diagnosticar():
    print("🧪 Ejecutando diagnóstico de indexación...")
    cargar_indice()
    fuentes = cargar_fuentes()
    selectores = cargar_selectores()

    for linea in fuentes:
        partes = [p.strip() for p in linea.split("|") if p.strip()]
        url = partes[0]
        tipo = "pagina"
        max_paginas = 50
        for p in partes[1:]:
            if p.startswith("tipo="): tipo = p.split("=")[1].strip()
            if p.startswith("max_paginas="):
                try:
                    max_paginas = int(p.split("=")[1].strip())
                except: pass

        if tipo == "sitemap":
            urls = obtener_urls_desde_sitemap(url, max_paginas=max_paginas)
        elif tipo == "dominio":
            urls = crawl_dominio(url, max_paginas=max_paginas)
        else:
            urls = [url]

        print(f"
🌐 Fuente: {url} ({tipo}) → {len(urls)} URLs encontradas")
        for u in urls[:3]:  # mostrar solo las 3 primeras URLs
            fragmentos = extraer_texto_web(u, selectores)
            print(f"🔍 {u} → {len(fragmentos)} fragmentos")
            if fragmentos:
                ejemplo = fragmentos[0].replace("\n", " ").replace("\r", " ")
                print("📌 Ejemplo:")
                print(ejemplo[:300])

    print(f"
📦 Fragmentos en el índice actual: {len(metadata)}")
    urls_indexadas = list(set(m["origen"] for m in metadata))
    print(f"🔗 URLs distintas indexadas: {len(urls_indexadas)}")

if __name__ == "__main__":
    diagnosticar()
