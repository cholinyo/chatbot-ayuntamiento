# app/domain_crawler.py

"""
Este módulo permite obtener automáticamente URLs internas desde un sitemap.xml
asociado a un dominio municipal (ej. https://www.ayuntamiento.es/sitemap.xml).
Es una alternativa más precisa y limpia al rastreo por enlaces HTML.
"""

import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

load_dotenv()


def obtener_urls_desde_sitemap(url_sitemap: str, dominio_filtrado: str = None, max_paginas: int = 50) -> list:
    """
    Obtiene URLs desde un archivo sitemap XML.

    Parámetros:
        url_sitemap (str): URL completa del sitemap.xml
        dominio_filtrado (str): dominio que deben contener las URLs (opcional)
        max_paginas (int): número máximo de URLs a devolver

    Retorna:
        list: lista de URLs contenidas en el sitemap
    """
    urls = []
    try:
        print(f"📄 Descargando sitemap: {url_sitemap}")
        response = requests.get(url_sitemap, timeout=10)
        response.raise_for_status()
        xml_content = response.content

        tree = ET.fromstring(xml_content)

        for url in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            loc = url.text.strip()
            if dominio_filtrado:
                if dominio_filtrado in urlparse(loc).netloc:
                    urls.append(loc)
            else:
                urls.append(loc)
            if len(urls) >= max_paginas:
                break

        print(f"✅ {len(urls)} URLs extraídas del sitemap.")

    except Exception as e:
        print(f"❌ Error al procesar el sitemap {url_sitemap}: {e}")

    return urls


# Ejemplo de uso:
if __name__ == "__main__":
    DOMINIO = os.getenv("DOMINIO_AYUNTAMIENTO", "https://www.ayuntamiento.es")
    SITEMAP_URL = f"{DOMINIO.rstrip('/')}/sitemap.xml"
    dominio_base = urlparse(DOMINIO).netloc
    urls = obtener_urls_desde_sitemap(SITEMAP_URL, dominio_filtrado=dominio_base, max_paginas=20)
    for u in urls:
        print(u)
