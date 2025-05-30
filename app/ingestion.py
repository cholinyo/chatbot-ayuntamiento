# app/ingestion.py actualizado con Selenium y fallback

from bs4 import BeautifulSoup
import requests
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import logging

MIN_LONGITUD_FRAGMENTO = 30  # caracteres mínimos por fragmento

# Función principal

def extraer_texto_web(url: str, selectores: List[str] = None) -> List[str]:
    if selectores is None:
        selectores = ['p', 'h1', 'h2', 'h3', 'article', 'section', 'div']

    html = obtener_html_con_selenium(url)
    if html is None:
        html = obtener_html_con_requests(url)

    if html is None:
        logging.warning(f"❌ No se pudo obtener contenido de: {url}")
        return []

    return extraer_fragmentos(html, selectores)


def obtener_html_con_requests(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.warning(f"⚠️ Error con requests en {url}: {e}")
        return None


def obtener_html_con_selenium(url: str) -> str:
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(15)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        return html
    except WebDriverException as e:
        logging.warning(f"⚠️ Selenium no pudo procesar {url}: {e}")
        return None


def extraer_fragmentos(html: str, selectores: List[str]) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')
    fragmentos = []
    for selector in selectores:
        elementos = soup.select(selector)
        for el in elementos:
            texto = el.get_text(strip=True)
            if len(texto) >= MIN_LONGITUD_FRAGMENTO:
                fragmentos.append(texto)
    return fragmentos
