"""
dbpedia.py
----------
Módulo de conexión al endpoint SPARQL remoto de DBpedia.
Usa XML (application/sparql-results+xml) — NO JSON.
"""

import requests
import xml.etree.ElementTree as ET

DBPEDIA_SPARQL   = "https://dbpedia.org/sparql"
DBPEDIA_TIMEOUT  = 15
_HEADERS = {
    "Accept": "application/sparql-results+xml",
    "User-Agent": "BuscadorSemanticoCelulares/2.0 (universidad)"
}

_SPARQL_XML_NS = "http://www.w3.org/2005/sparql-results#"

# Mapeo manual: nombre local en la ontología → recurso exacto en DBpedia
_MAPA_DBPEDIA: dict[str, str] = {
    "iPhone_14":              "IPhone_14",
    "iPhone_15_Pro":          "IPhone_15_Pro",
    "Samsung_Galaxy_S24":     "Samsung_Galaxy_S24",
    "Samsung_Galaxy_A54":     "Samsung_Galaxy_A54",
    "Xiaomi_13":              "Xiaomi_13",
    "Xiaomi_Redmi_Note_12":   "Redmi_Note_12",
    "Xiaomi_Redmi_Note_11":   "Redmi_Note_11",
    "Huawei_P60_Pro":         "Huawei_P60_Pro",
    "Huawei_Nova_11":         "Huawei_nova_11",
    "Motorola_Edge_40":       "Motorola_Edge_40",
    "Motorola_G73":           "Motorola_Moto_G73",
    "OnePlus_11":             "OnePlus_11",
    "OnePlus_Nord_3":         "OnePlus_Nord_3",
    "Oppo_Find_X5":           "OPPO_Find_X5",
    "Oppo_Reno_10":           "OPPO_Reno10",
}


# ═══════════════════════════════════════════════════════════════════════════════
# PARSEO XML SPARQL
# ═══════════════════════════════════════════════════════════════════════════════

def _parsear_xml_sparql(xml_text: str) -> dict:
    """Parsea una respuesta SPARQL en formato XML y retorna dict con filas/columnas."""
    try:
        root = ET.fromstring(xml_text)
        ns   = _SPARQL_XML_NS

        # Variables (columnas)
        head  = root.find(f"{{{ns}}}head")
        vars_ = [v.attrib["name"] for v in head.findall(f"{{{ns}}}variable")] if head is not None else []

        # Filas
        results = root.find(f"{{{ns}}}results")
        filas   = []
        if results is not None:
            for binding_el in results.findall(f"{{{ns}}}result"):
                fila = {}
                for b in binding_el.findall(f"{{{ns}}}binding"):
                    nombre = b.attrib.get("name", "")
                    # Puede ser <uri>, <literal>, <bnode>
                    for child in b:
                        fila[nombre] = child.text or ""
                        break
                filas.append({v: fila.get(v, "") for v in vars_})

        return {"columnas": vars_, "filas": filas, "total": len(filas)}

    except ET.ParseError as e:
        return {"columnas": [], "filas": [], "total": 0, "error": f"Error parseando XML: {e}"}
    except Exception as e:
        return {"columnas": [], "filas": [], "total": 0, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# CONSULTA SPARQL GENÉRICA
# ═══════════════════════════════════════════════════════════════════════════════

def consultar_dbpedia(sparql_query: str) -> dict:
    """Ejecuta una consulta SPARQL en DBpedia usando XML. Retorna dict con filas/columnas."""
    try:
        response = requests.get(
            DBPEDIA_SPARQL,
            params={"query": sparql_query, "format": "application/sparql-results+xml"},
            headers=_HEADERS,
            timeout=DBPEDIA_TIMEOUT
        )
        response.raise_for_status()
        return _parsear_xml_sparql(response.text)
    except requests.exceptions.Timeout:
        return {"columnas": [], "filas": [], "total": 0,
                "error": "DBpedia no respondió a tiempo (timeout)."}
    except requests.exceptions.ConnectionError:
        return {"columnas": [], "filas": [], "total": 0,
                "error": "Sin conexión a DBpedia."}
    except Exception as e:
        return {"columnas": [], "filas": [], "total": 0, "error": str(e)}


def _https(url: str) -> str:
    """Convierte URLs http:// de DBpedia a https:// para evitar mixed-content."""
    return url.replace("http://", "https://") if url else ""


# ═══════════════════════════════════════════════════════════════════════════════
# BUSCAR CELULARES EN DBPEDIA POR TEXTO LIBRE
# ═══════════════════════════════════════════════════════════════════════════════

def buscar_celulares_dbpedia(termino: str, lang: str = "es") -> list[dict]:
    """
    Busca celulares en DBpedia cuyo label contenga el término dado.
    Retorna lista de dicts con: uri_recurso, nombre, descripcion, imagen, fabricante, so, anio.
    El parámetro lang controla el idioma del abstract/descripción devuelto.
    El label siempre se busca en inglés (es el más completo en DBpedia),
    pero la descripción se pide en el idioma solicitado con fallback a inglés.
    """
    if lang not in ("es", "en", "pt"):
        lang = "es"
    termino_safe = termino.replace('"', '').replace("'", "")
    query = f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?recurso ?nombre ?descripcion ?imagen ?wikiPage WHERE {{
  ?recurso a dbo:MobilePhone ;
           rdfs:label ?nombre .
  FILTER(CONTAINS(LCASE(STR(?nombre)), LCASE("{termino_safe}")))
  FILTER(LANG(?nombre) = "en")
  OPTIONAL {{
    ?recurso dbo:abstract ?descripcion .
    FILTER(LANG(?descripcion) = "{lang}")
  }}
  OPTIONAL {{ ?recurso dbo:thumbnail ?imagen . }}
  OPTIONAL {{ ?recurso foaf:isPrimaryTopicOf ?wikiPage . }}
}}
LIMIT 12
"""
    raw = consultar_dbpedia(query)
    if raw.get("error") or raw["total"] == 0:
        # fallback: búsqueda sin filtro de tipo (más amplia)
        query2 = f"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?recurso ?nombre ?descripcion ?imagen ?wikiPage WHERE {{
  ?recurso rdfs:label ?nombre .
  FILTER(CONTAINS(LCASE(STR(?nombre)), LCASE("{termino_safe}")))
  FILTER(LANG(?nombre) = "en")
  ?recurso a ?tipo .
  FILTER(?tipo IN (dbo:MobilePhone, dbo:Device))
  OPTIONAL {{
    ?recurso dbo:abstract ?descripcion .
    FILTER(LANG(?descripcion) = "{lang}")
  }}
  OPTIONAL {{ ?recurso dbo:thumbnail ?imagen . }}
  OPTIONAL {{ ?recurso foaf:isPrimaryTopicOf ?wikiPage . }}
}}
LIMIT 12
"""
        raw = consultar_dbpedia(query2)

    resultados = []
    for fila in raw.get("filas", []):
        uri = fila.get("recurso", "")
        nombre_recurso = uri.split("/")[-1] if "/" in uri else uri
        resultados.append({
            "uri_recurso":    _https(uri),
            "nombre_recurso": nombre_recurso,
            "nombre":         fila.get("nombre", nombre_recurso.replace("_", " ")),
            "descripcion":    fila.get("descripcion", ""),
            "imagen":         _https(fila.get("imagen", "")),
            "enlace_wiki":    _https(fila.get("wikiPage", "")),
            "enlace_dbpedia": _https(uri),
            "fuente":         "DBpedia",
        })
    return resultados


# ═══════════════════════════════════════════════════════════════════════════════
# BUSCAR INFO ENRIQUECIDA DE UN CELULAR (para detalle local)
# ═══════════════════════════════════════════════════════════════════════════════

def buscar_en_dbpedia(uri_local: str) -> dict:
    """
    Busca información de un celular en DBpedia.
    Intenta primero con el mapeo manual, luego por label.
    """
    recurso = _MAPA_DBPEDIA.get(uri_local)
    if recurso:
        resultado = _consulta_por_recurso(recurso)
        if resultado.get("encontrado"):
            return resultado

    nombre = uri_local.replace("_", " ")
    return _consulta_por_label(nombre)


def _consulta_por_recurso(nombre_recurso: str) -> dict:
    """Consulta DBpedia por recurso exacto usando XML. Prioriza español, fallback inglés."""

    q_es = f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?descripcion ?imagen ?wikiPage ?fabricante ?so ?anio WHERE {{
  dbr:{nombre_recurso} dbo:abstract ?descripcion .
  FILTER(LANG(?descripcion) = "es")
  OPTIONAL {{ dbr:{nombre_recurso} dbo:thumbnail ?imagen . }}
  OPTIONAL {{ dbr:{nombre_recurso} foaf:isPrimaryTopicOf ?wikiPage . }}
  OPTIONAL {{
    dbr:{nombre_recurso} dbo:manufacturer ?fabObj .
    ?fabObj rdfs:label ?fabricante .
    FILTER(LANG(?fabricante) = "es" || LANG(?fabricante) = "en")
  }}
  OPTIONAL {{
    dbr:{nombre_recurso} dbo:operatingSystem ?soObj .
    ?soObj rdfs:label ?so .
    FILTER(LANG(?so) = "en")
  }}
  OPTIONAL {{ dbr:{nombre_recurso} dbo:releaseDate ?anio . }}
}}
LIMIT 1
"""
    raw = consultar_dbpedia(q_es)

    if not raw.get("error") and raw["total"] > 0 and raw["filas"][0].get("descripcion"):
        fila = raw["filas"][0]
    else:
        q_en = q_es.replace('LANG(?descripcion) = "es"', 'LANG(?descripcion) = "en"')
        raw2 = consultar_dbpedia(q_en)
        if raw2.get("error") or raw2["total"] == 0 or not raw2["filas"][0].get("descripcion"):
            q_meta = f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?imagen ?wikiPage ?fabricante ?so WHERE {{
  OPTIONAL {{ dbr:{nombre_recurso} dbo:thumbnail ?imagen . }}
  OPTIONAL {{ dbr:{nombre_recurso} foaf:isPrimaryTopicOf ?wikiPage . }}
  OPTIONAL {{
    dbr:{nombre_recurso} dbo:manufacturer ?fabObj .
    ?fabObj rdfs:label ?fabricante .
    FILTER(LANG(?fabricante) = "en")
  }}
  OPTIONAL {{
    dbr:{nombre_recurso} dbo:operatingSystem ?soObj .
    ?soObj rdfs:label ?so .
    FILTER(LANG(?so) = "en")
  }}
}}
LIMIT 1
"""
            raw_meta = consultar_dbpedia(q_meta)
            fila = raw_meta["filas"][0] if raw_meta["total"] > 0 else {}
        else:
            fila = raw2["filas"][0]

    imagen     = _https(fila.get("imagen", ""))
    wiki       = _https(fila.get("wikiPage", ""))
    desc       = fila.get("descripcion", "")
    fabricante = fila.get("fabricante", "")
    so         = fila.get("so", "")
    anio       = fila.get("anio", "")[:4] if fila.get("anio") else ""
    encontrado = bool(imagen or desc or wiki)

    return {
        "encontrado":        encontrado,
        "descripcion":       desc,
        "imagen":            imagen,
        "enlace_wiki":       wiki,
        "enlace_dbpedia":    f"https://dbpedia.org/resource/{nombre_recurso}",
        "fabricante":        fabricante,
        "sistema_operativo": so,
        "anio_lanzamiento":  anio,
        "fuente":            "DBpedia",
        "recurso":           nombre_recurso,
    }


def _consulta_por_label(nombre: str) -> dict:
    """Búsqueda por etiqueta cuando no hay mapeo exacto, usando XML."""
    query = f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?recurso ?descripcion ?imagen ?wikiPage WHERE {{
  ?recurso a dbo:MobilePhone ;
           rdfs:label ?label .
  FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{nombre}")))
  FILTER(LANG(?label) = "en")
  OPTIONAL {{
    ?recurso dbo:abstract ?descripcion .
    FILTER(LANG(?descripcion) = "es")
  }}
  OPTIONAL {{ ?recurso dbo:thumbnail ?imagen . }}
  OPTIONAL {{ ?recurso foaf:isPrimaryTopicOf ?wikiPage . }}
}}
LIMIT 1
"""
    raw = consultar_dbpedia(query)
    if raw.get("error") or raw["total"] == 0:
        return {"encontrado": False, "error": raw.get("error", f"No encontrado en DBpedia: '{nombre}'")}

    fila = raw["filas"][0]
    uri_recurso    = fila.get("recurso", "")
    nombre_recurso = uri_recurso.split("/")[-1] if "/" in uri_recurso else uri_recurso
    imagen         = _https(fila.get("imagen", ""))
    wiki           = _https(fila.get("wikiPage", ""))
    desc           = fila.get("descripcion", "")

    return {
        "encontrado":        bool(imagen or desc or wiki),
        "descripcion":       desc,
        "imagen":            imagen,
        "enlace_wiki":       wiki,
        "enlace_dbpedia":    _https(uri_recurso) or f"https://dbpedia.org/resource/{nombre_recurso}",
        "fabricante":        "",
        "sistema_operativo": "",
        "anio_lanzamiento":  "",
        "fuente":            "DBpedia (búsqueda por label)",
        "recurso":           nombre_recurso,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ENRIQUECER CELULAR
# ═══════════════════════════════════════════════════════════════════════════════

def enriquecer_celular(uri_local: str, datos_locales: dict) -> dict:
    info_dbpedia = buscar_en_dbpedia(uri_local)
    datos_locales["DBpedia"] = info_dbpedia
    return datos_locales


# ═══════════════════════════════════════════════════════════════════════════════
# CONSULTAS DBPEDIA PREDEFINIDAS
# ═══════════════════════════════════════════════════════════════════════════════

CONSULTAS_DBPEDIA = [
    {
        "id": "db1",
        "titulo": "Celulares en DBpedia",
        "descripcion": "Lista dispositivos móviles registrados en DBpedia con su etiqueta en español.",
        "sparql": """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?dispositivo ?nombre WHERE {
  ?dispositivo a dbo:MobilePhone ;
               rdfs:label ?nombre .
  FILTER(LANG(?nombre) = "es")
}
LIMIT 20"""
    },
    {
        "id": "db2",
        "titulo": "Fabricantes de smartphones en DBpedia",
        "descripcion": "Obtiene los fabricantes de teléfonos móviles conocidos en DBpedia.",
        "sparql": """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?fabricante ?nombre WHERE {
  ?tel a dbo:MobilePhone ;
       dbo:manufacturer ?fabricante .
  ?fabricante rdfs:label ?nombre .
  FILTER(LANG(?nombre) = "es")
}
LIMIT 20"""
    },
    {
        "id": "db3",
        "titulo": "Descripción del Samsung Galaxy S24 en DBpedia",
        "descripcion": "Obtiene el abstract en español del Samsung Galaxy S24 desde DBpedia.",
        "sparql": """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>
SELECT ?descripcion WHERE {
  dbr:Samsung_Galaxy_S24 dbo:abstract ?descripcion .
  FILTER(LANG(?descripcion) = "es")
}"""
    },
    {
        "id": "db4",
        "titulo": "Descripción del iPhone 14 en DBpedia",
        "descripcion": "Obtiene el abstract en español del iPhone 14 desde DBpedia.",
        "sparql": """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>
SELECT ?descripcion WHERE {
  dbr:IPhone_14 dbo:abstract ?descripcion .
  FILTER(LANG(?descripcion) = "es")
}"""
    },
    {
        "id": "db5",
        "titulo": "Smartphones lanzados en 2023 (DBpedia)",
        "descripcion": "Lista teléfonos cuyo año de lanzamiento sea 2023 según DBpedia.",
        "sparql": """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?tel ?nombre ?fecha WHERE {
  ?tel a dbo:MobilePhone ;
       rdfs:label ?nombre ;
       dbo:releaseDate ?fecha .
  FILTER(LANG(?nombre) = "en")
  FILTER(YEAR(?fecha) = 2023)
}
LIMIT 20"""
    },
]
