# Metabuscador Semántico de Teléfonos Celulares
**Web Semánticas 2026 · Ontología OWL + DBpedia + Multilingualidad**

---

## Requisitos previos

Antes de instalar, asegurate de tener:

- **Python 3.10 o superior** — verificar con `python --version` o `python3 --version`
- **Conexión a internet** — necesaria para consultar DBpedia en tiempo real

---

## Instalación

### 1. Descomprimir el proyecto

Descomprimir el archivo entregado y entrar a la carpeta:

```bash
cd metabuscador
```

### 2. (Recomendado) Crear un entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install flask rdflib requests
```

Eso es todo. El proyecto no usa ninguna base de datos externa ni servidor adicional.

---

## Estructura del proyecto

```
metabuscador/
│
├── app.py                    ← Punto de entrada, servidor Flask
├── ontology.py               ← Carga la ontología OWL en memoria
├── sparql_engine.py          ← Motor de búsqueda semántico SPARQL
├── nlp.py                    ← Procesamiento de lenguaje natural
├── dbpedia.py                ← Conexión con el endpoint SPARQL de DBpedia
├── queries.py                ← 80 consultas SPARQL predefinidas
├── poblar_dbpedia.py         ← Módulo de poblado desde DBpedia
│
├── ontologiaCelulares.rdf    ← Ontología OWL (NO mover ni renombrar)
│
├── static/
│   ├── css/                  ← Estilos de la interfaz
│   └── js/
│       └── app.js            ← Lógica de la interfaz web
│
└── templates/
    └── index.html            ← Página principal (SPA)
```

---

## Arrancar la aplicación

Desde la carpeta del proyecto, con el entorno virtual activado:

```bash
python app.py
```

Luego abrir el navegador en:

```
http://localhost:5000
```

---

## Funcionalidades disponibles

| Vista | Descripción |
|-------|-------------|
| 🔍 **Buscador** | Búsqueda semántica en lenguaje natural sobre la ontología local + resultados de DBpedia en paralelo |
| ⚡ **80 Consultas SPARQL** | Consultas predefinidas agrupadas por categoría, ejecutables con un clic |
| 🌐 **Explorador DBpedia** | Buscar celulares en DBpedia y agregarlos a la ontología local |
| 🗣 **Ontología Multilingüe** | Ver clases y propiedades OWL en español, inglés o portugués |

---

## Cambio de idioma

El botón de idioma en la barra superior (🇧🇴 ES / 🇺🇸 EN / 🇧🇷 PT) cambia:
- Los textos de la interfaz (botones, etiquetas, mensajes)
- El contenido consultado desde la ontología (clases, propiedades, detalle de celulares)

---

## Dependencias

| Librería | Versión mínima | Para qué se usa |
|----------|---------------|-----------------|
| `flask` | 2.0+ | Servidor web |
| `rdflib` | 6.0+ | Cargar y consultar la ontología OWL con SPARQL |
| `requests` | 2.0+ | Comunicación con el endpoint SPARQL de DBpedia |

---
