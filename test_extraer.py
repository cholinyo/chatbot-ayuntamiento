# test_extraer.py

from app.ingestion import extraer_texto_web

# Lista de URLs de prueba
pruebas = [
    {
        "url": "https://www.onda.es/index.php?contenido=apartado&id_boto=14200",
        "selectores": ["h1", "h2", "p", "div", "table"]
    },
    {
        "url": "https://www.onda.es/ond/web_php/index.php",
        "selectores": ["h1", "h2", "p", "div", "table"]
    },
    {
        "url": "https://www.onda.es/index.php?contenido=apartado&id_boto=15000",
        "selectores": ["h1", "h2", "p", "div", "table"]
    }
]

if __name__ == "__main__":
    for prueba in pruebas:
        print("=" * 80)
        print(f"🔍 Probando extracción desde: {prueba['url']}")
        fragmentos = extraer_texto_web(prueba["url"], prueba["selectores"])
        print(f"✅ {len(fragmentos)} fragmentos extraídos.\n")
        for i, f in enumerate(fragmentos[:3]):  # solo los 3 primeros
            print(f" • Fragmento {i+1}: {f[:200]}...\n")
