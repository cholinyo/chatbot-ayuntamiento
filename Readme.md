# Chatbot de Asistencia Ciudadana para Ayuntamiento

Este proyecto implementa un **chatbot de asistencia ciudadana**, diseñado para responder preguntas frecuentes de los ciudadanos a partir de datos oficiales del Ayuntamiento. El sistema está basado en una arquitectura **RAG (Retrieval-Augmented Generation)** y utiliza tecnologías locales y seguras, adecuadas para su despliegue en el entorno de una administración pública.

---

## 📚 Objetivos del Proyecto

- Atender consultas frecuentes de ciudadanos (horarios, procedimientos, documentos, etc.)
- Aprender de varias fuentes: webs municipales, APIs de trámites administrativos
- Ofrecer respuestas contextuales basadas en información real indexada
- Cumplir requisitos de seguridad según las guías del CCN-CERT
- Evitar la exposición de datos personales (PII)
- Facilitar la futura integración con un **grafo de conocimiento** institucional

---

## 🤖 Tecnologías Utilizadas

| Componente | Tecnología | Motivo de la elección |
|------------|------------|-------------------------|
| Web backend | **Flask** | Ligero, flexible y adecuado para apps RESTful seguras |
| Generación de embeddings | **Sentence Transformers** (`all-MiniLM-L6-v2`) | Rápido, preciso y ejecutable localmente |
| Vector DB (retrieval) | **FAISS** | Almacenamiento y recuperación de vectores eficiente y local |
| LLM (a integrar) | OpenAI / Llama2 / Mistral (opcional) | Dependiendo del entorno: nube o local |
| Interfaz web | HTML + JS | Para integración web sencilla con el backend Flask |
| Seguridad (futura) | Presidio / LLM Guard | Para detección y eliminación de datos personales |

---

## 📦 Estructura del Proyecto

```plaintext
chatbot-ayuntamiento/
├── app.py                      # Punto de entrada Flask
├── app/
│   ├── __init__.py
│   ├── rag_engine.py          # Módulo de RAG con FAISS
│   └── ingestion.py           # (próximo) carga de datos desde web/API
├── templates/
│   └── chat.html              # Interfaz de usuario web
├── static/                    # CSS y JS (opcional)
├── venv/                      # Entorno virtual (no incluido en repo)
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación y decisiones
```

---

## ✅ Decisiones Tomadas

- **FAISS** como motor vectorial: eficiente, local y compatible con entornos seguros.
- **Embeddings locales** con `sentence-transformers`: evita llamadas a terceros.
- **Flask** como backend: fácil de desplegar y controlar.
- Modularización del código: `app/` contiene lógica separada para escalar fácilmente.
- Interfaz web minimalista para pruebas iniciales: se podrá reemplazar por integraciones con sede electrónica o bots.

---

## 📖 Instrucciones de uso

1. Clona este repositorio y accede al directorio:
```bash
git clone https://github.com/tu-usuario/chatbot-ayuntamiento.git
cd chatbot-ayuntamiento
```

2. Crea un entorno virtual y actívalo:
```bash
python -m venv venv
venv\Scripts\activate    # En Windows
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación Flask:
```bash
python app.py
```

5. Accede desde el navegador a:
```
http://localhost:5000
```

---

## 🔄 Futuras ampliaciones

- [ ] Conexión a API REST de trámites administrativos
- [ ] Ingesta de contenido desde webs municipales (crawler limitado por dominio)
- [ ] Integración con grafo de conocimiento (Neo4j)
- [ ] Sistema de detección y eliminación de datos personales (PII)
- [ ] Reemplazo de LLM por modelos locales (Mistral, Llama2) ejecutados en Ollama
- [ ] Auditoría de seguridad según CCN-CERT

---

## 📈 Presentación futura

Este proyecto está siendo desarrollado con fines demostrativos para una futura presentación institucional sobre el uso de IA generativa en administraciones locales.

---

Si tienes preguntas o quieres colaborar, no dudes en contactar.

**Licencia**: MIT o conforme a las directrices municipales.

