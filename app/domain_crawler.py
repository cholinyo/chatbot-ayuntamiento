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

    def parsear_sitemap(url, depth=0):
        nonlocal urls
        try:
            if len(urls) >= max_paginas:
                return
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            xml_content = response.content
            tree = ET.fromstring(xml_content)

            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # Si es un sitemapindex (contiene otros sitemaps)
            if tree.tag.endswith("sitemapindex"):
                for sitemap in tree.findall("ns:sitemap", namespace):
                    loc_elem = sitemap.find("ns:loc", namespace)
                    if loc_elem is not None:
                        parsear_sitemap(loc_elem.text.strip(), depth + 1)

            # Si es un urlset (urls reales)
            elif tree.tag.endswith("urlset"):
                for url_elem in tree.findall("ns:url", namespace):
                    loc_elem = url_elem.find("ns:loc", namespace)
                    if loc_elem is not None:
                        loc = loc_elem.text.strip()
                        if dominio_filtrado:
                            if dominio_filtrado in urlparse(loc).netloc:
                                urls.append(loc)
                        else:
                            urls.append(loc)
                        if len(urls) >= max_paginas:
                            break

        except Exception as e:
            print(f"{'  '*depth}❌ Error al procesar {url}: {e}")

    print(f"📄 Descargando sitemap: {url_sitemap}")
    parsear_sitemap(url_sitemap)
    print(f"✅ {len(urls)} URLs extraídas del sitemap.")

    return urls


# app/domain_crawler.py

from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

def crawl_dominio(url_inicial: str, max_paginas: int = 50) -> list:
    visitadas = set()
    pendientes = [url_inicial]
    urls_resultado = []
    dominio_raiz = urlparse(url_inicial).netloc.replace("www.", "")  # Permite onda.es y www.onda.es

    print(f"🌍 Iniciando crawling en: {url_inicial} (dominio base: {dominio_raiz})")

    while pendientes and len(urls_resultado) < max_paginas:
        url = pendientes.pop(0)
        if url in visitadas:
            continue

        try:
            print(f"🔎 Visitando: {url}")
            resp = requests.get(url, timeout=10)
            if 'text/html' not in resp.headers.get('Content-Type', ''):
                print(f"   ⛔ No es HTML: {resp.headers.get('Content-Type')}")
                continue

            visitadas.add(url)
            urls_resultado.append(url)

            soup = BeautifulSoup(resp.text, 'html.parser')
            enlaces = soup.find_all('a', href=True)

            for enlace in enlaces:
                href = enlace['href'].strip()
                nueva_url = urljoin(url, href)
                parsed = urlparse(nueva_url)

                # Solo enlaces dentro del mismo dominio (quita subdominios extraños)
                if dominio_raiz in parsed.netloc.replace("www.", ""):
                    if nueva_url not in visitadas and nueva_url not in pendientes:
                        pendientes.append(nueva_url)

        except Exception as e:
            print(f"   ❌ Error al acceder a {url}: {e}")

    print(f"✅ Crawling finalizado: {len(urls_resultado)} URLs encontradas")
    return urls_resultado
