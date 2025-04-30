# app/ingestion.py

"""
Este módulo permite extraer contenido textual útil desde una página web oficial
del Ayuntamiento, para su posterior vectorización e indexación.
Usa requests y BeautifulSoup para hacer scraping básico y limpio.
"""

import requests
from bs4 import BeautifulSoup

def extraer_texto_web(url: str, selectores: list = None) -> list:
    """
    Extrae texto de una página web y lo convierte en fragmentos indexables.

    Parámetros:
        url (str): URL de la página web municipal a raspar
        selectores (list): lista opcional de etiquetas HTML a conservar 
                           (por defecto: ['p', 'h1', 'h2'])

    Retorna:
        list: fragmentos limpios de texto extraído
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        # Etiquetas por defecto si no se especifican
        if selectores is None:
            selectores = ['p', 'h1', 'h2']

        fragmentos = []
        total_por_etiqueta = {}

        for tag in selectores:
            elementos = soup.find_all(tag)
            total_por_etiqueta[tag] = 0
            for elemento in elementos:
                texto = elemento.get_text(strip=True)
                if texto and len(texto) > 30:  # Ignora fragmentos muy cortos
                    fragmentos.append(texto)
                    total_por_etiqueta[tag] += 1

        print(f"🔍 {url} → {len(fragmentos)} fragmentos extraídos.")
        for etiqueta, cantidad in total_por_etiqueta.items():
            print(f"   • {etiqueta}: {cantidad} fragmentos")

        return fragmentos

    except Exception as e:
        print(f"❌ Error al procesar la URL {url}: {e}")
        return []

# Prueba manual del módulo (ejecutable directo)
if __name__ == "__main__":
    url = "https://www.onda.es/"
    fragmentos = extraer_texto_web(url, selectores=['p', 'h1', 'h2', 'article', 'section', 'div'])
    for i, f in enumerate(fragmentos[:5]):
        print(f"\nFragmento {i+1}:\n{f}")
