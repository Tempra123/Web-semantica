"""
app.py
------
Punto de entrada de la aplicación Flask.
"""

from flask import Flask, render_template, request, jsonify, redirect
from ontology import OWL_FILE, NS_URI, g
from sparql_engine import (
    buscar_celulares,
    detalle_celular,
    estadisticas,
    ejecutar_consulta_raw,
)
from queries import get_all_queries, CATEGORIAS
from dbpedia import (
    buscar_en_dbpedia,
    buscar_celulares_dbpedia,
    consultar_dbpedia,
    CONSULTAS_DBPEDIA,
)
from nlp import interpretar_consulta
import re
from rdflib import URIRef, Literal, RDF, OWL, Namespace
from rdflib.namespace import XSD

app = Flask(__name__)

ALL_QUERIES   = get_all_queries(NS_URI)
QUERIES_BY_ID = {q["id"]: q for q in ALL_QUERIES}


# ═══════════════════════════════════════════════════════════════════════════════
# RUTAS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", stats=estadisticas())


@app.route("/consultas-sparql")
def consultas_page():
    return redirect("/#consultas")


@app.route("/buscar")
def buscar():
    termino = request.args.get("q", "").strip()
    filtro  = request.args.get("filtro", "todos")
    lang    = request.args.get("lang", "es").strip().lower()
    if lang not in ("es", "en", "pt"):
        lang = "es"
    resultados, filtros_detectados = buscar_celulares(termino, filtro, lang=lang)
    return jsonify({
        "resultados":         resultados,
        "total":              len(resultados),
        "filtros_detectados": filtros_detectados,
        "sugerencias":        filtros_detectados.get("sugerencias", []),
    })


@app.route("/detalle/<path:uri>")
def detalle(uri: str):
    lang = request.args.get("lang", "es")
    datos = detalle_celular(uri, lang=lang)
    return jsonify(datos)


# ═══════════════════════════════════════════════════════════════════════════════
# API DBPEDIA
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/dbpedia/celular/<path:uri>")
def dbpedia_celular(uri: str):
    info = buscar_en_dbpedia(uri)
    return jsonify(info)


@app.route("/api/dbpedia/buscar")
def dbpedia_buscar():
    """Busca celulares en DBpedia por texto libre.
    Parámetros: q (término), lang (es/en/pt, default es)
    """
    termino = request.args.get("q", "").strip()
    lang    = request.args.get("lang", "es").strip().lower()
    if lang not in ("es", "en", "pt"):
        lang = "es"
    if not termino:
        return jsonify({"resultados": [], "total": 0, "error": "Falta parámetro 'q'"})

    # Extraer término relevante para DBpedia usando el NLP.
    # Si la consulta tiene marca/modelo detectado, usar eso.
    # De lo contrario usar el texto limpio sin palabras de relleno.
    filtros = interpretar_consulta(termino, lang=lang)
    termino_dbp = (
        filtros.get("marca") or
        filtros.get("modelo") or
        filtros.get("texto_libre") or
        termino
    )
    # Si el término extraído es muy corto o vacío, usar el original
    if not termino_dbp or len(termino_dbp.strip()) < 2:
        termino_dbp = termino

    resultados = buscar_celulares_dbpedia(termino_dbp.strip(), lang=lang)
    return jsonify({"resultados": resultados, "total": len(resultados)})


@app.route("/api/dbpedia/agregar", methods=["POST"])
def dbpedia_agregar():
    """
    Agrega un celular desde DBpedia a la ontología local con TODAS sus características,
    usando los parsers de poblar_dbpedia.py (batería, pantalla, CPU, cámara, memoria, etc.)
    Espera JSON con: nombre_recurso (y opcionalmente nombre, imagen, enlace_dbpedia)
    """
    from poblar_dbpedia import (
        fetch_dbpedia_json,
        extraer_desde_dbpedia,
        Poblador,
        rdf_uri,
    )
    from rdflib.namespace import RDFS

    datos_req = request.get_json(force=True) or {}
    nombre_recurso = datos_req.get("nombre_recurso", "").strip()
    nombre_display = datos_req.get("nombre", nombre_recurso.replace("_", " ")).strip()

    if not nombre_recurso:
        return jsonify({"ok": False, "error": "Falta nombre_recurso"}), 400

    NS_local = Namespace(NS_URI)

    # Nombre local del individuo: usamos nombre_recurso + _DBpedia para evitar colisiones
    nombre_local = nombre_recurso + "_DBpedia"
    uri_nuevo = URIRef(NS_URI + nombre_local)

    # Verificar si ya existe
    if (uri_nuevo, RDF.type, NS_local.Celular) in g:
        return jsonify({"ok": True, "mensaje": f"'{nombre_display}' ya estaba en la ontología.", "ya_existia": True})

    try:
        # Extraer datos completos desde DBpedia usando los parsers de poblar_dbpedia
        datos = extraer_desde_dbpedia(nombre_recurso)

        if not datos:
            return jsonify({"ok": False, "error": f"No se encontraron datos en DBpedia para '{nombre_recurso}'"}), 404

        # Usar el Poblador de poblar_dbpedia para agregar el celular con todos sus componentes
        poblador = Poblador(g)
        agregado = poblador.agregar_celular(nombre_local, datos)

        if not agregado:
            return jsonify({"ok": True, "mensaje": f"'{nombre_display}' ya estaba en la ontología.", "ya_existia": True})

        # Agregar metadatos extra del card de DBpedia (imagen, enlace, fuente)
        imagen = datos_req.get("imagen", "")
        if imagen:
            g.add((uri_nuevo, NS_local.imagenDBpedia, Literal(imagen)))

        enlace = datos_req.get("enlace_dbpedia", "")
        if enlace:
            g.add((uri_nuevo, NS_local.enlaceDBpedia, Literal(enlace)))

        g.add((uri_nuevo, NS_local.fuenteDBpedia, Literal("true")))

        # Persistir en el archivo RDF
        fmt = "xml" if OWL_FILE and OWL_FILE.endswith(".rdf") else "turtle"
        g.serialize(destination=OWL_FILE, format=fmt)

        # Construir resumen de lo que se guardó
        campos_guardados = [k for k, v in datos.items()
                            if v not in ("--", False, [], "") and k != "abstract" and k != "sensores"]
        def _v(key):
            """Devuelve el valor o None si es '--' o vacío."""
            v = datos.get(key, "--")
            return None if v in ("--", "", None) else v

        return jsonify({
            "ok":               True,
            "mensaje":          f"'{nombre_display}' agregado a la ontología con {len(campos_guardados)} características.",
            "uri":              str(uri_nuevo),
            "campos_guardados": campos_guardados,
            "marca":            _v("marca"),
            "modelo":           _v("modelo") or nombre_display,
            "anio":             _v("anio"),
            "gama":             _v("gama"),
            "so":               _v("so"),
            "bateria_mah":      _v("bateria_mah"),
            "pantalla_tipo":    _v("pantalla_tipo"),
            "pantalla_pulgadas":_v("pantalla_pulgadas"),
            "pantalla_hz":      _v("pantalla_hz"),
            "cpu":              _v("cpu_modelo"),
            "ram_gb":           _v("ram_gb"),
            "storage_gb":       _v("storage_gb"),
            "camara_trasera_mp":_v("camara_trasera_mp"),
            "red_movil":        _v("red_movil"),
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/dbpedia/consultas")
def dbpedia_consultas_lista():
    return jsonify(CONSULTAS_DBPEDIA)


@app.route("/api/dbpedia/consulta/<string:qid>")
def dbpedia_ejecutar_consulta(qid: str):
    consulta = next((c for c in CONSULTAS_DBPEDIA if c["id"] == qid), None)
    if not consulta:
        return jsonify({"error": f"Consulta '{qid}' no encontrada"}), 404
    resultado = consultar_dbpedia(consulta["sparql"])
    resultado["titulo"] = consulta["titulo"]
    resultado["descripcion_consulta"] = consulta["descripcion"]
    return jsonify(resultado)


@app.route("/api/dbpedia/sparql")
def dbpedia_sparql_libre():
    sparql = request.args.get("q", "").strip()
    if not sparql:
        return jsonify({"error": "Falta el parámetro 'q'"}), 400
    return jsonify(consultar_dbpedia(sparql))


# ═══════════════════════════════════════════════════════════════════════════════
# API CONSULTAS LOCALES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/consultas")
def lista_consultas():
    por_categoria: dict = {}
    for cat in CATEGORIAS:
        por_categoria[cat] = [
            {
                "id":          q["id"],
                "titulo":      q["titulo"],
                "descripcion": q["descripcion"],
                "tipo":        q["tipo"],
                "categoria":   q["categoria"],
            }
            for q in ALL_QUERIES if q["categoria"] == cat
        ]
    return jsonify({"categorias": CATEGORIAS, "consultas": por_categoria})


@app.route("/api/consulta/<int:qid>")
def ejecutar_consulta(qid: int):
    if qid not in QUERIES_BY_ID:
        return jsonify({"error": f"Consulta {qid} no encontrada"}), 404
    q = QUERIES_BY_ID[qid]
    resultado = ejecutar_consulta_raw(q["sparql"])
    resultado.update({k: q[k] for k in ("id", "titulo", "descripcion", "categoria", "sparql")})
    return jsonify(resultado)


# ═══════════════════════════════════════════════════════════════════════════════
# API MULTILINGUALIDAD — rdfs:label con @lang
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/ontologia/etiquetas")
def ontologia_etiquetas():
    """
    Devuelve clases y propiedades con rdfs:label, rdfs:comment,
    rdfs:domain, rdfs:range, rdfs:subClassOf, owl:inverseOf
    en el idioma solicitado (es / en / pt).
    """
    lang = request.args.get("lang", "es").lower()
    if lang not in ("es", "en", "pt"):
        lang = "es"

    def ejecutar_clases():
        sparql = f"""
            PREFIX owl:  <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?entidad ?label ?comment ?padre WHERE {{
                ?entidad a owl:Class .
                OPTIONAL {{ ?entidad rdfs:label   ?label   . FILTER(lang(?label)   = "{lang}") }}
                OPTIONAL {{ ?entidad rdfs:comment ?comment . FILTER(lang(?comment) = "{lang}") }}
                OPTIONAL {{ ?entidad rdfs:subClassOf ?padre .
                            FILTER(!isBlank(?padre)) }}
            }} ORDER BY ?entidad
        """
        filas = []
        for row in g.query(sparql):
            nombre = str(row.entidad).split("#")[-1]
            padre  = str(row.padre).split("#")[-1] if row.padre else ""
            filas.append({
                "uri":     str(row.entidad),
                "nombre":  nombre,
                "label":   str(row.label)   if row.label   else nombre,
                "comment": str(row.comment) if row.comment else "",
                "padre":   padre,
            })
        return filas

    def ejecutar_obj_props():
        sparql = f"""
            PREFIX owl:  <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?entidad ?label ?comment ?dominio ?rango ?inversa WHERE {{
                ?entidad a owl:ObjectProperty .
                OPTIONAL {{ ?entidad rdfs:label   ?label   . FILTER(lang(?label)   = "{lang}") }}
                OPTIONAL {{ ?entidad rdfs:comment ?comment . FILTER(lang(?comment) = "{lang}") }}
                OPTIONAL {{ ?entidad rdfs:domain  ?dominio . FILTER(!isBlank(?dominio)) }}
                OPTIONAL {{ ?entidad rdfs:range   ?rango   . FILTER(!isBlank(?rango))   }}
                OPTIONAL {{ ?entidad owl:inverseOf ?inversa . FILTER(!isBlank(?inversa)) }}
            }} ORDER BY ?entidad
        """
        filas = []
        for row in g.query(sparql):
            nombre  = str(row.entidad).split("#")[-1]
            dominio = str(row.dominio).split("#")[-1] if row.dominio else ""
            rango   = str(row.rango).split("#")[-1]   if row.rango   else ""
            inversa = str(row.inversa).split("#")[-1] if row.inversa else ""
            filas.append({
                "uri":     str(row.entidad),
                "nombre":  nombre,
                "label":   str(row.label)   if row.label   else nombre,
                "comment": str(row.comment) if row.comment else "",
                "dominio": dominio,
                "rango":   rango,
                "inversa": inversa,
            })
        return filas

    def ejecutar_dato_props():
        sparql = f"""
            PREFIX owl:  <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?entidad ?label ?comment ?dominio ?rango WHERE {{
                ?entidad a owl:DatatypeProperty .
                OPTIONAL {{ ?entidad rdfs:label   ?label   . FILTER(lang(?label)   = "{lang}") }}
                OPTIONAL {{ ?entidad rdfs:comment ?comment . FILTER(lang(?comment) = "{lang}") }}
                OPTIONAL {{ ?entidad rdfs:domain  ?dominio . FILTER(!isBlank(?dominio)) }}
                OPTIONAL {{ ?entidad rdfs:range   ?rango   . FILTER(!isBlank(?rango))   }}
            }} ORDER BY ?entidad
        """
        filas = []
        for row in g.query(sparql):
            nombre  = str(row.entidad).split("#")[-1]
            dominio = str(row.dominio).split("#")[-1] if row.dominio else ""
            rango_raw = str(row.rango) if row.rango else ""
            # Simplify XSD types: xsd:integer → integer
            rango = rango_raw.split("#")[-1] if "#" in rango_raw else rango_raw.split("/")[-1] if rango_raw else ""
            filas.append({
                "uri":     str(row.entidad),
                "nombre":  nombre,
                "label":   str(row.label)   if row.label   else nombre,
                "comment": str(row.comment) if row.comment else "",
                "dominio": dominio,
                "rango":   rango,
            })
        return filas

    clases     = ejecutar_clases()
    props_obj  = ejecutar_obj_props()
    props_dato = ejecutar_dato_props()

    def ejecutar_individuos():
        sparql = f"""
            PREFIX owl:  <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?entidad ?label ?comment ?tipo WHERE {{
                ?entidad a owl:NamedIndividual .
                OPTIONAL {{ ?entidad rdfs:label   ?label   . FILTER(lang(?label)   = "{lang}") }}
                OPTIONAL {{ ?entidad rdfs:comment ?comment . FILTER(lang(?comment) = "{lang}") }}
                OPTIONAL {{
                    ?entidad a ?tipo .
                    FILTER(?tipo != owl:NamedIndividual && !isBlank(?tipo))
                }}
            }} ORDER BY ?tipo ?entidad
        """
        filas = {}
        for row in g.query(sparql):
            uri = str(row.entidad)
            if uri not in filas:
                nombre = uri.split("#")[-1]
                filas[uri] = {
                    "uri":     uri,
                    "nombre":  nombre,
                    "label":   str(row.label)   if row.label   else nombre,
                    "comment": str(row.comment) if row.comment else "",
                    "tipo":    str(row.tipo).split("#")[-1] if row.tipo else "",
                }
            elif row.tipo and not filas[uri]["tipo"]:
                filas[uri]["tipo"] = str(row.tipo).split("#")[-1]
        return list(filas.values())

    individuos = ejecutar_individuos()

    return jsonify({
        "lang":  lang,
        "clases": clases,
        "propiedades_objeto": props_obj,
        "propiedades_dato":   props_dato,
        "individuos": individuos,
        "totales": {
            "clases":              len(clases),
            "propiedades_objeto":  len(props_obj),
            "propiedades_dato":    len(props_dato),
            "individuos":          len(individuos),
        },
    })


@app.route("/debug")
def debug():
    info = {
        "archivo":         OWL_FILE,
        "tripletas":       len(g),
        "namespace":       NS_URI,
        "namespaces":      {p: str(u) for p, u in g.namespaces()},
        "clases":          [],
        "total_consultas": len(ALL_QUERIES),
    }
    try:
        for row in g.query(
            "SELECT DISTINCT ?c WHERE { ?c rdf:type <http://www.w3.org/2002/07/owl#Class> }"
        ):
            info["clases"].append(str(row.c))
    except Exception as e:
        info["error"] = str(e)
    return jsonify(info)


if __name__ == "__main__":
    app.run(debug=True, port=5000)