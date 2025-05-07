# app/ingestion.py

"""
Este módulo permite extraer contenido textual útil desde una página web oficial
del Ayuntamiento, para su posterior vectorización e indexación.
Usa requests y BeautifulSoup para hacer scraping básico y limpio.
"""

import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def extraer_texto_web(url: str, selectores: list) -> list:
    def analizar_con_bs(html: str, origen: str) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        fragmentos = []
        for selector in selectores:
            elementos = soup.select(selector)
            for el in elementos:
                texto = el.get_text(separator=" ", strip=True)
                if texto:
                    fragmentos.append(texto)
        print(f"   • {origen}: {len(fragmentos)} fragmentos extraídos con {', '.join(selectores)}")
        return fragmentos

    try:
        # Primer intento: requests
        print(f"🌐 Descargando (requests): {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Detectar redirección por <meta http-equiv="refresh">
        soup = BeautifulSoup(response.text, 'html.parser')
        refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
        if refresh and "URL=" in refresh.get("content", ""):
            redir_url = refresh["content"].split("URL=")[-1].strip()
            url = urljoin(url, redir_url)
            print(f"🔁 Redireccionando a: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

        # Intentar extracción con BeautifulSoup
        fragmentos = analizar_con_bs(response.text, "BeautifulSoup")
        if fragmentos:
            return fragmentos

    except Exception as e:
        print(f"⚠️ Error con requests: {e}")

    # Plan B: Selenium si no se extrajo nada o hubo error
    try:
        print(f"🚗 Cargando con Selenium: {url}")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        html = driver.page_source
        driver.quit()

        fragmentos = analizar_con_bs(html, "Selenium")
        return fragmentos

    except Exception as e:
        print(f"❌ Selenium falló: {e}")
        return []


# Prueba manual del módulo
if __name__ == "__main__":
    url = "https://www.onda.es/noticias/actualidad"
    fragmentos = extraer_texto_web(
        url,
        selectores=['p', 'h1', 'h2', 'article', 'section', 'li']
    )

    print(f"\nFragmentos extraídos: {len(fragmentos)}")
    for i, f in enumerate(fragmentos[:5]):
        print(f"\n--- Fragmento {i+1} ---\n{f}")
