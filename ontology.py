"""
ontology.py
-----------
Responsabilidad única: cargar el archivo RDF/OWL y detectar el namespace base.

Todo el resto de la app importa `g` (el grafo) y `NS_URI` (el IRI base)
desde aquí, de modo que la ontología solo se parsea UNA vez al arrancar.
"""

import os
from rdflib import Graph, Namespace, RDF, OWL

# ── Archivos candidatos (varios nombres/extensiones posibles) ─────────────────
_POSIBLES_ARCHIVOS = [
    "ontologiaCelulares_ampliada.rdf",
    "ontologiaCelulares.rdf", "ontologia_celulares.rdf",
    "ontologia_celulares.owl", "ontologiaCelulares.owl",
    "ontologia_celulares.ttl", "ontologiaCelulares.ttl",
]

# Mapeo extensión → formato rdflib
_FMT_MAP = {".rdf": "xml", ".owl": "xml", ".ttl": "turtle",
            ".n3": "n3", ".jsonld": "json-ld"}

# ── Buscar el archivo de ontología junto al propio módulo ─────────────────────
_BASE_DIR = os.path.dirname(__file__)
OWL_FILE: str | None = None

for _nombre in _POSIBLES_ARCHIVOS:
    _candidato = os.path.join(_BASE_DIR, _nombre)
    if os.path.exists(_candidato):
        OWL_FILE = _candidato
        break

# ── Crear y cargar el grafo ───────────────────────────────────────────────────
g = Graph()

if OWL_FILE is None:
    print("✗ No se encontró el archivo de ontología.")
else:
    try:
        _ext = os.path.splitext(OWL_FILE)[1].lower()
        g.parse(OWL_FILE, format=_FMT_MAP.get(_ext, "xml"))
        print(f"✓ Ontología cargada: {OWL_FILE} ({len(g)} tripletas)")
    except Exception as _e:
        print(f"✗ Error cargando ontología: {_e}")


def detectar_namespace() -> str:
    """
    Infiere el IRI base de la ontología examinando los tipos de los individuos.

    Estrategia:
    1. Cuenta cuántas veces aparece cada namespace en ?rdf:type → toma el más frecuente
       (ignorando namespaces estándar de RDF/OWL/XSD).
    2. Si no hay individuos, busca la declaración owl:Ontology.
    3. Fallback al IRI hardcodeado del proyecto.
    """
    candidatos: dict[str, int] = {}
    for _s, _p, o in g.triples((None, RDF.type, None)):
        ns = (str(o).rsplit("#", 1)[0] + "#" if "#" in str(o)
              else str(o).rsplit("/", 1)[0] + "/")
        candidatos[ns] = candidatos.get(ns, 0) + 1

    if candidatos:
        ignorar = ["rdf-syntax", "rdf-schema", "owl#", "xmlschema"]
        filtrado = {k: v for k, v in candidatos.items()
                    if not any(ig in k for ig in ignorar)}
        if filtrado:
            return max(filtrado, key=filtrado.get)

    # Fallback: buscar declaración owl:Ontology
    for s, _p, _o in g.triples((None, RDF.type, OWL.Ontology)):
        base = str(s)
        return base if base.endswith("#") else base + "#"

    return "http://www.semanticweb.org/nagha/ontologies/2026/3/untitled-ontology-25#"


# ── IRI base y Namespace rdflib ───────────────────────────────────────────────
NS_URI: str      = detectar_namespace()
NS:     Namespace = Namespace(NS_URI)