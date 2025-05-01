# app/domain_crawler.py

"""
Este módulo permite obtener URLs desde un sitemap.xml o rastrear enlaces internos
empezando desde una URL base del dominio.
"""

import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

load_dotenv()

def obtener_urls_desde_sitemap(url_sitemap: str, dominio_filtrado: str = None, max_paginas: int = 50) -> list:
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

def crawl_dominio(url_inicial: str, max_paginas: int = 50) -> list:
    visitadas = set()
    pendientes = [url_inicial]
    dominio = urlparse(url_inicial).netloc

    while pendientes and len(visitadas) < max_paginas:
        url = pendientes.pop(0)
        if url in visitadas:
            continue

        try:
            resp = requests.get(url, timeout=10)
            if 'text/html' not in resp.headers.get('Content-Type', ''):
                continue

            visitadas.add(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            enlaces = soup.find_all('a', href=True)

            for enlace in enlaces:
                href = enlace['href']
                nueva_url = urljoin(url, href)
                parsed = urlparse(nueva_url)
                if parsed.netloc == dominio and nueva_url not in visitadas:
                    pendientes.append(nueva_url)

        except Exception as e:
            print(f"❌ Error accediendo a {url}: {e}")

    return list(visitadas)
