"""
sparql_engine.py
----------------
Construye y ejecuta consultas SPARQL sobre el grafo RDF.

MEJORAS v2:
  - ORDER BY dinámico: cuando precio_modo = "rango" o "minimo" ordena
    ASC por precio (más baratos primero dentro del rango).
    Cuando precio_modo = "maximo" ordena DESC (más caros primero, ya que
    el usuario tiene presupuesto y quiere lo mejor).
    Sin filtro de precio: orden por marca/modelo.
  - Igual para almacenamiento, RAM, batería: si el usuario pide un valor
    que no existe exacto, el NLP ya hizo el snap; aquí sólo necesitamos
    que el ORDER BY sea consistente.
  - Nuevo campo en resultados: "precio_modo" propagado desde filtros,
    para que la UI sepa cómo presentar la lista (badge "desde X").

Funciones públicas:
  buscar_celulares(termino, filtro_gama) → (lista_resultados, filtros_dict)
  detalle_celular(uri_local)             → dict agrupado de propiedades
  estadisticas()                         → dict con métricas del grafo
  ejecutar_consulta_raw(sparql_str)      → dict tipado (SELECT o ASK)
"""

import re
from ontology import g, NS_URI
from nlp import interpretar_consulta, PALABRAS_RUIDO, PALABRAS_RUIDO_EN, PALABRAS_RUIDO_PT, _normalizar


# ═══════════════════════════════════════════════════════════════════════════════
# BÚSQUEDA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def buscar_celulares(termino: str = "", filtro_gama: str = "todos", lang: str = "es"):
    """
    Traduce texto libre + gama en una consulta SPARQL dinámica y la ejecuta.

    Retorna:
      (lista[dict], filtros_dict)
      - lista[dict]: cada dict con atributos del celular + precio_modo.
      - filtros_dict: resultado de nlp.interpretar_consulta (para badges).

    Lógica de precio (nueva):
    ─────────────────────────
    precio_modo = "rango"   → ORDER BY ASC(?precio)   (desde el precio snapped)
    precio_modo = "minimo"  → ORDER BY ASC(?precio)   (desde el mínimo pedido)
    precio_modo = "maximo"  → ORDER BY DESC(?precio)  (lo mejor dentro del presupuesto)
    None                    → ORDER BY ?marca ?modelo  (comportamiento original)
    """
    filtros = interpretar_consulta(termino, lang=lang) if termino else {}

    partes_filter: list[str] = []
    joins_extra:   list[str] = []

    # ── GAMA ──────────────────────────────────────────────────────────────────
    gama_efectiva = filtros.get("gama") or (filtro_gama if filtro_gama != "todos" else None)
    if gama_efectiva:
        partes_filter.append(
            f'FILTER(LCASE(STR(?gama)) = LCASE("{gama_efectiva}"))')

    # ── SISTEMA OPERATIVO ─────────────────────────────────────────────────────
    if filtros.get("so"):
        partes_filter.append(
            f'FILTER(CONTAINS(LCASE(STR(?so)), LCASE("{filtros["so"]}")  ))')

    # ── MARCA ─────────────────────────────────────────────────────────────────
    if filtros.get("marca"):
        partes_filter.append(
            f'FILTER(LCASE(STR(?marca)) = LCASE("{filtros["marca"]}"))')

    # ── RAM exacta / min / max ────────────────────────────────────────────────
    if filtros.get("ram"):
        partes_filter.append(
            f'FILTER(STRDT(STR(?ram), xsd:integer) = {filtros["ram"]})')
    if filtros.get("ram_min"):
        partes_filter.append(
            f'FILTER(STRDT(STR(?ram), xsd:integer) >= {filtros["ram_min"]})')
    if filtros.get("ram_max"):
        partes_filter.append(
            f'FILTER(STRDT(STR(?ram), xsd:integer) <= {filtros["ram_max"]})')

    # ── ALMACENAMIENTO INTERNO ────────────────────────────────────────────────
    # "almacenamiento" aquí puede ser exacto O snapped al real superior.
    # Usamos >= para que si el snap movió el valor, no queden cero resultados.
    if filtros.get("almacenamiento"):
        partes_filter.append(
            f'FILTER(STRDT(STR(?almacenamiento), xsd:integer) >= {filtros["almacenamiento"]})')

    # ── MICRO-SD ──────────────────────────────────────────────────────────────
    if filtros.get("microsd") == "true":
        partes_filter.append('FILTER(STR(?microsd) = "true")')
    elif filtros.get("microsd") == "false":
        partes_filter.append('FILTER(STR(?microsd) = "false")')

    # ── PRECIO (USD) — rango numérico ─────────────────────────────────────────
    if filtros.get("precio_min"):
        partes_filter.append(f'FILTER(?precio >= {filtros["precio_min"]})')
    if filtros.get("precio_max"):
        partes_filter.append(f'FILTER(?precio <= {filtros["precio_max"]})')

    # ── AÑO ───────────────────────────────────────────────────────────────────
    if filtros.get("anio_min"):
        partes_filter.append(f'FILTER(STRDT(STR(?anio), xsd:integer) >= {filtros["anio_min"]})')
    if filtros.get("anio_max"):
        partes_filter.append(f'FILTER(STRDT(STR(?anio), xsd:integer) <= {filtros["anio_max"]})')

    # ── CPU — marca del procesador ─────────────────────────────────────────────
    if filtros.get("cpu"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneProcesador ?cpuObj .
            ?cpuObj :marcaCPU ?marcaCPUf .
            FILTER(CONTAINS(LCASE(STR(?marcaCPUf)), LCASE("{filtros['cpu']}")))
        }}""")

    # ── TIPO DE PANTALLA ──────────────────────────────────────────────────────
    if filtros.get("pantalla"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tienePantalla ?panObjF .
            ?panObjF :tipoPantalla ?tipoPantallaF .
            FILTER(CONTAINS(LCASE(STR(?tipoPantallaF)), LCASE("{filtros['pantalla']}")))
        }}""")

    # ── TAMAÑO DE PANTALLA ────────────────────────────────────────────────────
    if filtros.get("pantalla_min"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tienePantalla ?panMinObj .
            ?panMinObj :tamanoPantalla ?tamPanMin .
            FILTER(STRDT(STR(?tamPanMin), xsd:integer) >= {filtros['pantalla_min']})
        }}""")
    if filtros.get("pantalla_max"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tienePantalla ?panMaxObj .
            ?panMaxObj :tamanoPantalla ?tamPanMax .
            FILTER(STRDT(STR(?tamPanMax), xsd:integer) <= {filtros['pantalla_max']})
        }}""")

    # ── TASA DE REFRESCO ──────────────────────────────────────────────────────
    if filtros.get("refresco"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tienePantalla ?panRefObj .
            ?panRefObj :tasaRefresco ?tasaRefF .
            FILTER(STRDT(STR(?tasaRefF), xsd:integer) = {filtros['refresco']})
        }}""")
    if filtros.get("refresco_min"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tienePantalla ?panRefMinObj .
            ?panRefMinObj :tasaRefresco ?tasaRefMin .
            FILTER(STRDT(STR(?tasaRefMin), xsd:integer) >= {filtros['refresco_min']})
        }}""")

    # ── BATERÍA — capacidad ───────────────────────────────────────────────────
    if filtros.get("bateria_min") or filtros.get("bateria_max"):
        conds = []
        if filtros.get("bateria_min"):
            conds.append(f"STRDT(STR(?capReq), xsd:integer) >= {filtros['bateria_min']}")
        if filtros.get("bateria_max"):
            conds.append(f"STRDT(STR(?capReq), xsd:integer) <= {filtros['bateria_max']}")
        cond_str = " && ".join(conds)
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneBateria ?batReqObj .
            ?batReqObj :capacidad ?capReq .
            FILTER({cond_str})
        }}""")

    # ── CARGA RÁPIDA ──────────────────────────────────────────────────────────
    if filtros.get("carga_rapida"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneBateria ?batCRObj .
            ?batCRObj :cargaRapida ?cargaRapidaF .
            FILTER(STR(?cargaRapidaF) = "{filtros['carga_rapida']}")
        }}""")

    # ── CARGA INALÁMBRICA ─────────────────────────────────────────────────────
    if filtros.get("carga_inalambrica"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneBateria ?batCIObj .
            ?batCIObj :cargaInalambrica ?cargaInaF .
            FILTER(STR(?cargaInaF) = "{filtros['carga_inalambrica']}")
        }}""")

    # ── RED MÓVIL ─────────────────────────────────────────────────────────────
    if filtros.get("red"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneRedMovil ?redMObj .
            ?redMObj :tipoRedMovil ?tipoRedF .
            FILTER(CONTAINS(LCASE(STR(?tipoRedF)), LCASE("{filtros['red']}")))
        }}""")
    if filtros.get("red_excl"):
        joins_extra.append(f"""
        FILTER NOT EXISTS {{
            ?celular :tieneRedMovil ?redExclObj .
            ?redExclObj :tipoRedMovil ?redExclTipo .
            FILTER(CONTAINS(LCASE(STR(?redExclTipo)), LCASE("{filtros['red_excl']}")))
        }}""")

    # ── NFC ───────────────────────────────────────────────────────────────────
    if filtros.get("nfc") == "true":
        joins_extra.append("""
        FILTER EXISTS {
            ?celular :tieneRedInalambrica ?nfcObj .
            ?nfcObj :tipoRedInalambrica "NFC" .
        }""")
    elif filtros.get("nfc") == "false":
        joins_extra.append("""
        FILTER NOT EXISTS {
            ?celular :tieneRedInalambrica ?nfcExObj .
            ?nfcExObj :tipoRedInalambrica "NFC" .
        }""")

    # ── WIFI ──────────────────────────────────────────────────────────────────
    if filtros.get("wifi"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneRedInalambrica ?wifiObj .
            ?wifiObj :tipoRedInalambrica ?wifiTipoF .
            FILTER(CONTAINS(LCASE(STR(?wifiTipoF)), LCASE("{filtros['wifi']}")))
        }}""")

    # ── TIPO SIM ──────────────────────────────────────────────────────────────
    if filtros.get("sim"):
        joins_extra.append(f"""
        ?celular :tieneTipoSIM :{filtros['sim']} .""")
    if filtros.get("sim_excl"):
        joins_extra.append(f"""
        FILTER NOT EXISTS {{ ?celular :tieneTipoSIM :{filtros['sim_excl']} . }}""")

    # ── CÁMARA TRASERA ────────────────────────────────────────────────────────
    if filtros.get("camara_min"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneCamaraTrasera ?camTF .
            ?camTF :resolucionPrincipal ?resCamF .
            FILTER(STRDT(STR(?resCamF), xsd:integer) >= {filtros['camara_min']})
        }}""")
    if filtros.get("camara_max"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneCamaraTrasera ?camTMaxF .
            ?camTMaxF :resolucionPrincipal ?resCamMax .
            FILTER(STRDT(STR(?resCamMax), xsd:integer) <= {filtros['camara_max']})
        }}""")

    # ── CÁMARA FRONTAL ────────────────────────────────────────────────────────
    if filtros.get("camara_frontal_min"):
        joins_extra.append(f"""
        FILTER EXISTS {{
            ?celular :tieneCamaraFrontal ?camFF .
            ?camFF :resolucionFrontal ?resFrontalF .
            FILTER(STRDT(STR(?resFrontalF), xsd:integer) >= {filtros['camara_frontal_min']})
        }}""")

    # ── SENSORES ──────────────────────────────────────────────────────────────
    if filtros.get("sensor"):
        joins_extra.append(f"""
        ?celular :tieneSensor :{filtros['sensor']} .""")
    if filtros.get("sensor_excl"):
        joins_extra.append(f"""
        FILTER NOT EXISTS {{ ?celular :tieneSensor :{filtros['sensor_excl']} . }}""")

    # ── RESISTENCIA IP ────────────────────────────────────────────────────────
    if filtros.get("resistencia_exacta"):
        joins_extra.append(f"""
        ?celular :tieneResistencia ?resExObj .
        ?resExObj :certificacion "{filtros['resistencia_exacta']}" .""")
    elif filtros.get("resistencia"):
        val = filtros["resistencia"]
        joins_extra.append(f"""
        ?celular :tieneResistencia ?resObj2 .
        ?resObj2 :certificacion ?certF .
        FILTER(CONTAINS(LCASE(STR(?certF)), LCASE("{val}")))""")
    if filtros.get("resistencia_neg"):
        val = filtros["resistencia_neg"]
        joins_extra.append(f"""
        FILTER NOT EXISTS {{
            ?celular :tieneResistencia ?resNegObj .
            ?resNegObj :certificacion ?certNeg .
            FILTER(CONTAINS(LCASE(STR(?certNeg)), LCASE("{val}")))
        }}""")

    # ── AUDIO ─────────────────────────────────────────────────────────────────
    if filtros.get("audio"):
        val = filtros["audio"]
        joins_extra.append(f"""
        ?celular :tieneAudio ?audioFObj .
        ?audioFObj :tipoSalida ?tipoAudioF .
        FILTER(CONTAINS(LCASE(STR(?tipoAudioF)), LCASE("{val}")))""")
    if filtros.get("audio_neg"):
        val = filtros["audio_neg"]
        joins_extra.append(f"""
        FILTER NOT EXISTS {{
            ?celular :tieneAudio ?audioNegObj .
            ?audioNegObj :tipoSalida ?tipoAudioNeg .
            FILTER(CONTAINS(LCASE(STR(?tipoAudioNeg)), LCASE("{val}")))
        }}""")

    # ── BÚSQUEDA DE TEXTO LIBRE ───────────────────────────────────────────────
    filtros_activos = [k for k, v in filtros.items()
                       if v and k not in ("texto_libre", "sugerencias",
                                          "negaciones", "precio_modo")]
    if termino and not filtros_activos:
        t_clean = _normalizar(termino)
        _ruido_activo = PALABRAS_RUIDO_EN if lang == "en" else PALABRAS_RUIDO_PT if lang == "pt" else PALABRAS_RUIDO
        for ruido in _ruido_activo:
            t_clean = re.sub(rf'\b{re.escape(ruido)}\b', ' ', t_clean)
        t_clean = re.sub(r'\s+', ' ', t_clean).strip()
        if t_clean:
            partes_filter.append(f'''FILTER(
                CONTAINS(LCASE(STR(?marca)), LCASE("{t_clean}")) ||
                CONTAINS(LCASE(STR(?modelo)), LCASE("{t_clean}"))
            )''')

    # ── ORDER BY dinámico basado en precio_modo ────────────────────────────────
    # IMPORTANTE: usar STRDT para todas las variables numéricas con xsd:integer
    # mal declarado en la ontología; sin esto el orden es lexicográfico y
    # "1024" queda antes que "128".
    precio_modo = filtros.get("precio_modo")
    if precio_modo in ("rango", "minimo"):
        order_clause = "ORDER BY ASC(?precio) ?marca ?modelo"
    elif precio_modo == "maximo":
        order_clause = "ORDER BY DESC(?precio) ?marca ?modelo"
    elif filtros.get("camara_min"):
        order_clause = "ORDER BY ASC(STRDT(STR(?camTrasera), xsd:integer)) ?marca ?modelo"
    elif filtros.get("bateria_min"):
        order_clause = "ORDER BY ASC(STRDT(STR(?bateria), xsd:integer)) ?marca ?modelo"
    elif filtros.get("bateria_max"):
        order_clause = "ORDER BY DESC(STRDT(STR(?bateria), xsd:integer)) ?marca ?modelo"
    elif filtros.get("ram_min") or filtros.get("ram"):
        order_clause = "ORDER BY ASC(STRDT(STR(?ram), xsd:integer)) ?marca ?modelo"
    elif filtros.get("almacenamiento"):
        order_clause = "ORDER BY ASC(STRDT(STR(?almacenamiento), xsd:integer)) ?marca ?modelo"
    elif filtros.get("refresco_min") or filtros.get("refresco"):
        order_clause = "ORDER BY ASC(STRDT(STR(?tasaRefresco), xsd:integer)) ?marca ?modelo"
    else:
        order_clause = "ORDER BY ?marca ?modelo"

    # ── Ensamblar la consulta ──────────────────────────────────────────────────
    filtros_str = "\n        ".join(partes_filter)
    joins_str   = "\n        ".join(joins_extra)

    query = f"""
    PREFIX : <{NS_URI}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?celular ?marca ?modelo ?gama ?precio ?so ?ram ?almacenamiento ?anio
                    ?bateria ?cargaRapida ?cargaInalambrica ?microsd
                    ?tipoPantalla ?tamanoPantalla ?tasaRefresco
                    ?camTrasera ?camFrontal
                    ?redMovil ?certification ?fuenteDBpedia
    WHERE {{
        ?celular rdf:type :Celular .
        OPTIONAL {{ ?celular :fuenteDBpedia ?fuenteDBpedia }}
        OPTIONAL {{ ?celular :marcaCelular ?marca }}
        OPTIONAL {{ ?celular :modeloCelular ?modelo }}
        OPTIONAL {{ ?celular :gama ?gama }}
        OPTIONAL {{ ?celular :precio ?precio }}
        OPTIONAL {{ ?celular :anio ?anio }}
        OPTIONAL {{
            ?celular :tieneSistemaOperativo ?soUri .
            OPTIONAL {{ ?soUri :nombreSO ?soNombre }}
            BIND(COALESCE(?soNombre, REPLACE(STR(?soUri), "^.*[#/]", "")) AS ?so)
        }}
        OPTIONAL {{
            ?celular :tieneMemoria ?memObj .
            OPTIONAL {{ ?memObj :RAM ?ram }}
            OPTIONAL {{ ?memObj :almacenamientoInterno ?almacenamiento }}
            OPTIONAL {{ ?memObj :admiteMicroSD ?microsd }}
        }}
        OPTIONAL {{
            ?celular :tieneBateria ?batObj .
            OPTIONAL {{ ?batObj :capacidad ?bateria }}
            OPTIONAL {{ ?batObj :cargaRapida ?cargaRapida }}
            OPTIONAL {{ ?batObj :cargaInalambrica ?cargaInalambrica }}
        }}
        OPTIONAL {{
            ?celular :tienePantalla ?panObj .
            OPTIONAL {{ ?panObj :tipoPantalla ?tipoPantalla }}
            OPTIONAL {{ ?panObj :tamanoPantalla ?tamanoPantalla }}
            OPTIONAL {{ ?panObj :tasaRefresco ?tasaRefresco }}
        }}
        OPTIONAL {{
            ?celular :tieneCamaraTrasera ?ctObj .
            OPTIONAL {{ ?ctObj :resolucionPrincipal ?camTrasera }}
        }}
        OPTIONAL {{
            ?celular :tieneCamaraFrontal ?cfObj .
            OPTIONAL {{ ?cfObj :resolucionFrontal ?camFrontal }}
        }}
        OPTIONAL {{
            ?celular :tieneRedMovil ?rmUri .
            OPTIONAL {{ ?rmUri :tipoRedMovil ?redMovilNombre }}
            BIND(COALESCE(?redMovilNombre, REPLACE(STR(?rmUri), "^.*[#/]", "")) AS ?redMovil)
        }}
        OPTIONAL {{
            ?celular :tieneResistencia ?resObj .
            OPTIONAL {{ ?resObj :certificacion ?certification }}
        }}
        {joins_str}
        {filtros_str}
    }}
    {order_clause}
    LIMIT 200
    """

    try:
        resultados: list[dict] = []
        seen: set[str] = set()

        for row in g.query(query):
            uri_key = str(row.celular).split("#")[-1] if row.celular else ""
            if uri_key in seen:
                continue
            seen.add(uri_key)

            def _s(v): return str(v) if v is not None else "—"

            resultados.append({
                "uri":              uri_key,
                "marca":            _s(row.marca),
                "modelo":           _s(row.modelo),
                "gama":             _s(row.gama),
                "precio":           _s(row.precio),
                "so":               _s(row.so),
                "ram":              _s(row.ram),
                "almacenamiento":   _s(row.almacenamiento),
                "microsd":          _s(row.microsd),
                "anio":             _s(row.anio),
                "bateria":          _s(row.bateria),
                "cargaRapida":      _s(row.cargaRapida),
                "cargaInalambrica": _s(row.cargaInalambrica),
                "tipoPantalla":     _s(row.tipoPantalla),
                "tamanoPantalla":   _s(row.tamanoPantalla),
                "tasaRefresco":     _s(row.tasaRefresco),
                "camTrasera":       _s(row.camTrasera),
                "camFrontal":       _s(row.camFrontal),
                "redMovil":         _s(row.redMovil),
                "certificacion":    _s(row.certification),
                "fuenteDBpedia":    (str(row.fuenteDBpedia) == "true") if row.fuenteDBpedia is not None else False,
                # Meta: para que la UI sepa el modo
                "_precio_modo":     precio_modo or "ninguno",
                "_precio_snapped":  filtros.get("precio_min", "—"),
            })

        return resultados, filtros

    except Exception as e:
        print(f"Error SPARQL buscar_celulares: {e}")
        return [], {}


# ═══════════════════════════════════════════════════════════════════════════════
# DETALLE COMPLETO DE UN CELULAR
# ═══════════════════════════════════════════════════════════════════════════════

_PROPS_IGNORAR: set[str] = {
    "type", "esBateriaDe", "esMemoriaDe", "esProcesadorDe",
    "esPantallaDe", "esCamaraTraseraDe", "esCamaraFrontalDe",
    "esSistemaOperativoDe", "esAudioDe", "esRedMovilDe",
    "esRedInalambricaDe", "esSensorDe", "tieneProcesador",
    "tieneMemoria", "tieneBateria", "tienePantalla",
    "tieneCamaraTrasera", "tieneCamaraFrontal",
    "tieneSistemaOperativo", "tieneAudio", "tieneRedMovil",
    "tieneRedInalambrica", "tieneSensor", "tieneResistencia",
    "tieneTipoSIM",
    # Propiedades internas de DBpedia — no mostrar en el modal
    "fuenteDBpedia", "enlaceDBpedia", "imagenDBpedia",
    # rdfs:label redundante en componentes (Red Móvil, Pantalla, etc.)
    "label",
}

# ── Labels desde la ontología ──────────────────────────────────────────────────
# En vez de un mapa estático, cargamos rdfs:label @lang del grafo RDF.
# _PROP_LABELS[lang][local_name] → label traducido
# _GRUPO_LABELS[lang][nombre_es] → label traducido del grupo/clase

def _cargar_labels_ontologia() -> tuple[dict, dict]:
    """
    Precarga desde el grafo RDF:
      - labels de propiedades: ?prop rdfs:label ?lbl
      - labels de grupos/clases: ?clase rdfs:label ?lbl  (solo clases de componentes)
    Retorna (prop_labels, grupo_labels) indexados por lang → local_name → label.
    """
    LANGS = ("es", "en", "pt")
    prop_labels:  dict[str, dict[str, str]] = {l: {} for l in LANGS}
    grupo_labels: dict[str, dict[str, str]] = {l: {} for l in LANGS}

    query_props = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl:  <http://www.w3.org/2002/07/owl#>
    SELECT ?prop ?lbl WHERE {{
        ?prop a ?tipo .
        FILTER(?tipo IN (owl:DatatypeProperty, owl:ObjectProperty, owl:Class))
        ?prop rdfs:label ?lbl .
        FILTER(lang(?lbl) IN ("es","en","pt"))
    }}
    """
    try:
        for row in g.query(query_props):
            uri  = str(row.prop)
            name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
            lng  = str(row.lbl.language) if hasattr(row.lbl, "language") else "es"
            if lng in prop_labels:
                prop_labels[lng][name] = str(row.lbl)
    except Exception as e:
        print(f"[sparql_engine] Error cargando prop labels: {e}")

    # Grupos: clases de componentes con label en los 3 idiomas.
    # Mapeamos nombre en español (usado internamente) → label por lang.
    CLASES_GRUPOS = {
        "General":                  None,   # no es clase OWL, usamos label directo
        "Procesador":               "Procesador",
        "Memoria":                  "Memoria",
        "Batería":                  "Bateria",
        "Pantalla":                 "Pantalla",
        "Cámara Trasera":           "CamaraTrasera",
        "Cámara Frontal":           "CamaraFrontal",
        "Sistema Operativo":        "SistemaOperativo",
        "Audio":                    None,
        "Red Móvil":                "RedMovil",
        "Conectividad Inalámbrica": "RedInalambrica",
        "Sensores":                 "Sensor",
        "Resistencia":              "Resistencia",
        "SIM":                      "TipoSIM",
    }
    query_clases = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl:  <http://www.w3.org/2002/07/owl#>
    SELECT ?clase ?lbl WHERE {{
        ?clase a owl:Class .
        ?clase rdfs:label ?lbl .
        FILTER(lang(?lbl) IN ("es","en","pt"))
    }}
    """
    clase_labels: dict[str, dict[str, str]] = {}  # local_name → lang → label
    try:
        for row in g.query(query_clases):
            uri  = str(row.clase)
            name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
            lng  = str(row.lbl.language) if hasattr(row.lbl, "language") else "es"
            clase_labels.setdefault(name, {})[lng] = str(row.lbl)
    except Exception as e:
        print(f"[sparql_engine] Error cargando clase labels: {e}")

    for grupo_es, clase_name in CLASES_GRUPOS.items():
        if clase_name and clase_name in clase_labels:
            for lng, lbl in clase_labels[clase_name].items():
                if lng in grupo_labels:
                    grupo_labels[lng][grupo_es] = lbl

    return prop_labels, grupo_labels


# Cargamos una vez al importar el módulo
_PROP_LABELS, _GRUPO_LABELS = _cargar_labels_ontologia()


def _prop_label(prop_name: str, lang: str) -> str:
    """Devuelve el rdfs:label de una propiedad en el idioma pedido.
    Fallback: lang='es', luego el prop_name en crudo."""
    return (
        _PROP_LABELS.get(lang, {}).get(prop_name)
        or _PROP_LABELS.get("es", {}).get(prop_name)
        or prop_name
    )


def _grupo_label(grupo_es: str, lang: str) -> str:
    """Devuelve el rdfs:label del grupo/clase en el idioma pedido."""
    return (
        _GRUPO_LABELS.get(lang, {}).get(grupo_es)
        or _GRUPO_LABELS.get("es", {}).get(grupo_es)
        or grupo_es
    )

_GRUPOS_MULTI: set[str] = {"Sensores", "Conectividad Inalámbrica", "Red Móvil", "SIM"}


def detalle_celular(uri_local: str, lang: str = "es") -> dict:
    """Devuelve TODAS las propiedades de un celular, organizadas por componente."""
    query = f"""
    PREFIX : <{NS_URI}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?grupo ?prop ?valor
    WHERE {{
        {{
            ?celular rdf:type :Celular .
            FILTER(STRENDS(STR(?celular), "{uri_local}"))
            ?celular ?prop ?valor .
            FILTER(!isBlank(?valor))
            BIND("General" AS ?grupo)
        }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tieneProcesador ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Procesador" AS ?grupo) }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tieneMemoria ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Memoria" AS ?grupo) }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tieneBateria ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Batería" AS ?grupo) }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tienePantalla ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Pantalla" AS ?grupo) }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tieneCamaraTrasera ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Cámara Trasera" AS ?grupo) }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tieneCamaraFrontal ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Cámara Frontal" AS ?grupo) }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tieneSistemaOperativo ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Sistema Operativo" AS ?grupo) }}
        UNION {{
            ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
            ?celular :tieneAudio ?comp .
            OPTIONAL {{ ?comp rdfs:label ?lbl . FILTER(lang(?lbl) = "{lang}") }}
            BIND(COALESCE(?lbl, ?comp) AS ?valor)
            BIND(:tipoSalida AS ?prop)
            FILTER(BOUND(?valor)) BIND("Audio" AS ?grupo)
        }}
        UNION {{ ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
                 ?celular :tieneRedMovil ?comp . ?comp ?prop ?valor .
                 FILTER(!isBlank(?valor)) BIND("Red Móvil" AS ?grupo) }}
        UNION {{
            ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
            ?celular :tieneRedInalambrica ?comp .
            OPTIONAL {{ ?comp rdfs:label ?lbl . FILTER(lang(?lbl) = "{lang}") }}
            BIND(COALESCE(?lbl, ?comp) AS ?valor)
            BIND(:tipoRedInalambrica AS ?prop)
            FILTER(BOUND(?valor)) BIND("Conectividad Inalámbrica" AS ?grupo)
        }}
        UNION {{
            ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
            ?celular :tieneSensor ?comp .
            OPTIONAL {{ ?comp rdfs:label ?lbl . FILTER(lang(?lbl) = "{lang}") }}
            BIND(COALESCE(?lbl, ?comp) AS ?valor)
            BIND(:tipoSensor AS ?prop)
            FILTER(BOUND(?valor)) BIND("Sensores" AS ?grupo)
        }}
        UNION {{
            ?celular rdf:type :Celular . FILTER(STRENDS(STR(?celular), "{uri_local}"))
            ?celular :tieneResistencia ?comp .
            OPTIONAL {{ ?comp rdfs:label ?lbl . FILTER(lang(?lbl) = "{lang}") }}
            BIND(COALESCE(?lbl, ?comp) AS ?valor)
            BIND(:nombreResistencia AS ?prop)
            FILTER(BOUND(?valor)) BIND("Resistencia" AS ?grupo)
        }}
        UNION {{
            ?celular rdf:type :Celular .
            FILTER(STRENDS(STR(?celular), "{uri_local}"))
            ?celular :tieneTipoSIM ?comp .
            BIND(:TipoSIM AS ?prop)
            ?comp rdfs:label ?simLbl .
            FILTER(lang(?simLbl) = "{lang}")
            BIND(STR(?simLbl) AS ?valor)
            BIND("SIM" AS ?grupo)
        }}
        UNION {{
            ?celular rdf:type :Celular .
            FILTER(STRENDS(STR(?celular), "{uri_local}"))
            ?celular :tieneTipoSIM ?comp .
            FILTER NOT EXISTS {{ ?comp rdfs:label ?lbl . FILTER(lang(?lbl) = "{lang}") }}
            BIND(:TipoSIM AS ?prop)
            BIND(STR(?comp) AS ?valor)
            BIND("SIM" AS ?grupo)
        }}
    }}
    ORDER BY ?grupo ?prop
    """

    try:
        grupos: dict[str, dict] = {}
        grupos_acum: dict[str, tuple] = {}

        for row in g.query(query):
            grupo_es = str(row.grupo) if row.grupo else "General"
            raw_prop = str(row.prop)
            prop_name = (raw_prop.split("#")[-1] if "#" in raw_prop
                         else raw_prop.split("/")[-1])
            if prop_name in _PROPS_IGNORAR:
                continue

            valor = str(row.valor)
            valor_limpio = valor.split("#")[-1] if "#" in valor else valor

            if valor_limpio.lower() == "true":  valor_limpio = "__bool_true__"
            if valor_limpio.lower() == "false": valor_limpio = "__bool_false__"

            # Label de la propiedad desde la ontología (con fallback)
            label = _prop_label(prop_name, lang)
            # Label del grupo/sección desde la ontología
            grupo_label = _grupo_label(grupo_es, lang) or grupo_es

            if grupo_es in _GRUPOS_MULTI:
                key = f"{grupo_es}|{label}"
                if key not in grupos_acum:
                    grupos_acum[key] = (grupo_label, label, set())
                grupos_acum[key][2].add(valor_limpio)
            else:
                grupos.setdefault(grupo_label, {})[label] = valor_limpio

        for _key, (grupo_label, label, vals) in grupos_acum.items():
            grupos.setdefault(grupo_label, {})[label] = ", ".join(sorted(vals))

        # Añadimos la lista de grupos en el orden correcto para que el frontend
        # no tenga que re-mapear desde español.
        ORDEN_ES = [
            "General", "Procesador", "Memoria", "Batería", "Pantalla",
            "Cámara Trasera", "Cámara Frontal", "Sistema Operativo",
            "Audio", "Red Móvil", "Conectividad Inalámbrica",
            "Sensores", "Resistencia", "SIM",
        ]
        orden_traducido = [_grupo_label(g, lang) or g for g in ORDEN_ES]
        extras = [g for g in grupos if g not in orden_traducido]
        grupos["__grupos_orden__"] = orden_traducido + extras

        return grupos

    except Exception as e:
        print(f"Error detalle_celular: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADÍSTICAS DEL GRAFO
# ═══════════════════════════════════════════════════════════════════════════════

def estadisticas() -> dict:
    """Retorna métricas básicas del grafo: total celulares, clases y tripletas."""
    queries_stats = {
        "total_celulares": f"SELECT (COUNT(?c) AS ?n) WHERE {{ ?c rdf:type <{NS_URI}Celular> }}",
        "total_clases":    "SELECT (COUNT(DISTINCT ?c) AS ?n) WHERE { ?c rdf:type <http://www.w3.org/2002/07/owl#Class> }",
        "total_tripletas": "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }",
    }
    stats: dict = {}
    for k, q in queries_stats.items():
        try:
            for row in g.query(q):
                stats[k] = str(row[0])
        except Exception:
            stats[k] = "?"
    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN DE CONSULTAS SPARQL PREDEFINIDAS
# ═══════════════════════════════════════════════════════════════════════════════

def _limpiar_valor(v) -> str:
    s = str(v)
    if "#" in s:
        return s.split("#")[-1]
    if "/" in s:
        ultimo = s.rsplit("/", 1)[-1]
        if ultimo and not ultimo.startswith("http"):
            return ultimo
    return s


def ejecutar_consulta_raw(sparql_str: str) -> dict:
    """Ejecuta una cadena SPARQL arbitraria (SELECT o ASK)."""
    sparql_upper = sparql_str.strip().upper()

    if sparql_upper.startswith("ASK"):
        try:
            respuesta = bool(g.query(sparql_str))
            return {"tipo": "ASK", "respuesta": respuesta,
                    "texto": "SÍ" if respuesta else "NO"}
        except Exception as e:
            return {"tipo": "ASK", "respuesta": False, "texto": "Error", "error": str(e)}
    else:
        try:
            resultado = g.query(sparql_str)
            vars_ = [str(v) for v in resultado.vars]
            filas = []
            for row in resultado:
                fila = {
                    var: (_limpiar_valor(getattr(row, var))
                          if getattr(row, var) is not None else "—")
                    for var in vars_
                }
                filas.append(fila)
            return {"tipo": "SELECT", "columnas": vars_,
                    "filas": filas, "total": len(filas)}
        except Exception as e:
            return {"tipo": "SELECT", "columnas": [], "filas": [],
                    "total": 0, "error": str(e)}