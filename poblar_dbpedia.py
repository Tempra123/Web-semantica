#!/usr/bin/env python3
"""
poblar_dbpedia.py
======================
Pobla la ontología consultando DBpedia mediante SPARQL + respuesta XML.
No usa la API JSON de DBpedia en ningún momento.

Uso:
    python poblar_dbpedia.py

Requiere:
    pip install rdflib requests
"""

import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, RDF, OWL
from rdflib.namespace import XSD, RDFS
import requests

# ─── Config ────────────────────────────────────────────────────────────────────
ONTOLOGIA_ENTRADA = "ontologiaCelulares.rdf"
ONTOLOGIA_SALIDA  = "ontologiaCelulares_ampliada.rdf"
NS_URI = "http://www.semanticweb.org/nagha/ontologies/2026/3/untitled-ontology-25#"
NS     = Namespace(NS_URI)

DBPEDIA_SPARQL_URL = "http://dbpedia.org/sparql"
SPARQL_XML_NS      = "http://www.w3.org/2005/sparql-results#"
TIMEOUT = 30
HEADERS_SPARQL = {
    "User-Agent": "PobladorOntologiaCelulares/3.0 (universidad)",
    "Accept": "application/sparql-results+xml",
}

# Prefijos DBpedia
DBP       = "http://dbpedia.org/property/"
DBO       = "http://dbpedia.org/ontology/"
RDF_TYPE  = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
FOAF_NAME  = "http://xmlns.com/foaf/0.1/name"


# ═══════════════════════════════════════════════════════════════════════════════
# FETCH VÍA SPARQL + XML (sin JSON)
# ═══════════════════════════════════════════════════════════════════════════════

def _parsear_xml_sparql(xml_text: str) -> list[dict]:
    """
    Parsea respuesta XML del endpoint SPARQL de DBpedia.
    Retorna lista de filas: [{"p": "...", "o": "...", "type": "...", "lang": "..."}]
    """
    try:
        root = ET.fromstring(xml_text)
        ns   = SPARQL_XML_NS
        results = root.find(f"{{{ns}}}results")
        filas = []
        if results is None:
            return filas
        for result in results.findall(f"{{{ns}}}result"):
            fila = {}
            for binding in result.findall(f"{{{ns}}}binding"):
                nombre = binding.attrib.get("name", "")
                for child in binding:
                    tag = child.tag.split("}")[-1]  # uri, literal, bnode
                    fila[nombre] = {
                        "value": child.text or "",
                        "type":  "uri" if tag == "uri" else "literal",
                        "lang":  child.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", ""),
                    }
                    break
            if fila:
                filas.append(fila)
        return filas
    except ET.ParseError as e:
        print(f"    ⚠  Error parseando XML SPARQL: {e}")
        return []


def fetch_dbpedia_sparql(recurso: str) -> dict:
    """
    Obtiene todas las propiedades de un recurso DBpedia via SPARQL + XML.
    Retorna dict con estructura: {uri_propiedad: [{"value":..., "type":..., "lang":...}]}
    """
    uri = f"http://dbpedia.org/resource/{recurso}"
    query = f"""
SELECT ?p ?o WHERE {{
  <{uri}> ?p ?o .
  FILTER(isLiteral(?o) || isURI(?o))
}}
LIMIT 600
"""
    try:
        r = requests.get(
            DBPEDIA_SPARQL_URL,
            params={"query": query, "format": "application/sparql-results+xml"},
            headers=HEADERS_SPARQL,
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f"    ⚠  SPARQL HTTP {r.status_code}")
            return {}

        filas = _parsear_xml_sparql(r.text)
        if not filas:
            print(f"    ⚠  SPARQL vacío — '{recurso}' no existe en DBpedia")
            return {}

        # Seguir redirect (wikiPageRedirects)
        for fila in filas:
            p = fila.get("p", {}).get("value", "")
            o = fila.get("o", {})
            if p == "http://dbpedia.org/ontology/wikiPageRedirects":
                destino = o.get("value", "").split("/resource/")[-1]
                print(f"    → Redirect a {destino}")
                return fetch_dbpedia_sparql(destino)

        # Construir dict de propiedades
        props: dict = {}
        for fila in filas:
            p_val = fila.get("p", {}).get("value", "")
            o_val = fila.get("o", {})
            if p_val and o_val:
                props.setdefault(p_val, []).append(o_val)

        print(f"    ✅ SPARQL+XML OK — {len(props)} propiedades")
        return props

    except requests.exceptions.Timeout:
        print(f"    ⚠  SPARQL timeout")
        return {}
    except Exception as e:
        print(f"    ⚠  SPARQL error: {e}")
        return {}


# Alias para compatibilidad con app.py que importa fetch_dbpedia_json
def fetch_dbpedia_json(recurso: str) -> dict:
    """Alias — delega a fetch_dbpedia_sparql (no usa JSON)."""
    return fetch_dbpedia_sparql(recurso)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS DE EXTRACCIÓN (misma interfaz que antes)
# ═══════════════════════════════════════════════════════════════════════════════

def _vals(props: dict, prop_uri: str, lang: str = None) -> list[str]:
    entradas = props.get(prop_uri, [])
    resultado = []
    for e in entradas:
        v = str(e.get("value", ""))
        if not v:
            continue
        if lang is not None:
            if e.get("lang", "") == lang or e.get("lang", "") == "":
                resultado.append(v)
        else:
            resultado.append(v)
    return resultado


def _val(props: dict, prop_uri: str, lang: str = "en") -> str:
    vals = _vals(props, prop_uri, lang)
    return vals[0] if vals else "--"


def _todo_texto(props: dict) -> str:
    partes = []
    for entradas in props.values():
        for e in entradas:
            if e.get("type") == "literal":
                lang = e.get("lang", "")
                if lang in ("en", ""):
                    partes.append(str(e.get("value", "")))
    return " ".join(partes)


# ═══════════════════════════════════════════════════════════════════════════════
# PARSERS DE TEXTO LIBRE
# ═══════════════════════════════════════════════════════════════════════════════

def _num(texto: str, patron: str, grupo: int = 1) -> str:
    m = re.search(patron, texto, re.IGNORECASE)
    return m.group(grupo) if m else "--"


def parsear_bateria_mah(props: dict, todo: str) -> str:
    # dbp:battery puede ser: "3000 mAh", "21600.0" (en segundos), texto libre, o entero puro (mAh)
    # dbo:battery puede ser numérico (a veces en mAh, a veces en Wh)
    bats = _vals(props, DBP + "battery", "en")
    if not bats:
        bats = _vals(props, DBP + "battery")

    for b in bats:
        if not re.search(r'\+|ultra|fe\b|pro\+', b, re.IGNORECASE):
            m = re.search(r'(\d{3,5})\s*mah', b, re.IGNORECASE)
            if m:
                return m.group(1)
            # Número entero puro entre 1000-7000 → probablemente mAh
            m2 = re.search(r'^(\d{4,5})(?:\.0)?$', b.strip())
            if m2:
                val = int(float(b.strip()))
                if 1000 <= val <= 7000:
                    return str(val)

    # Buscar mAh en todo el texto del dispositivo
    m = re.search(r'(\d{3,5})\s*mah', todo, re.IGNORECASE)
    if m:
        return m.group(1)

    m2 = re.search(r'(\d{4,5})\s*[-–]?\s*mah', todo, re.IGNORECASE)
    if m2:
        return m2.group(1)

    # ← NUEVO: dbo:battery como numérico (algunos dispositivos lo guardan en mAh sin unidad)
    bat_dbo_vals = _vals(props, DBO + "battery")
    for bv in bat_dbo_vals:
        bv = bv.strip()
        try:
            val = int(float(bv))
            if 1000 <= val <= 7000:   # rango mAh realista
                return str(val)
        except:
            pass

    return "--"


def parsear_carga_w(props: dict, todo: str) -> str:
    carga = _val(props, DBP + "charging")
    if carga == "--":
        carga = todo
    m = re.search(r'(\d+)\s*w\b(?!\s*ireless)', carga, re.IGNORECASE)
    return m.group(1) if m else _num(todo, r'(\d+)\s*w\s*(?:fast|quick|super|wired)')


def parsear_carga_inalambrica(props: dict, todo: str) -> bool:
    carga = _val(props, DBP + "charging")
    # Solo buscar en el campo de carga, NO en todo el texto
    fuente = carga if carga != "--" else ""

    # Negaciones explícitas
    if re.search(r'no\s+wireless|without\s+wireless|does\s+not\s+support\s+wireless'
                 r'|no\s+qi|no\s+inalambr', fuente, re.IGNORECASE):
        return False

    # Detección positiva: solo en campo charging
    if re.search(r'wireless\s*charg|magsafe|qi\b|inalambr', fuente, re.IGNORECASE):
        return True

    return False


def parsear_pantalla(props: dict, todo: str) -> dict:
    display = _val(props, DBP + "display")
    screen  = _val(props, DBP + "screen")         # ← NUEVO
    res_dbo = _val(props, DBO + "screenResolution") # ← NUEVO (numérico en px)

    # ← NUEVO: recoger TODOS los valores de dbp:display (algunos modelos tienen
    #   el tipo en un valor y las pulgadas en otro, ej A05: "PLS LCD" separado de "6.7 inches")
    display_vals = _vals(props, DBP + "display", "en")
    if not display_vals:
        display_vals = _vals(props, DBP + "display")
    display_multi = " ".join(display_vals)

    # ← NUEVO: dbo:abstract y dbp:screenSize como fuentes adicionales
    screensize_vals = _vals(props, DBP + "screenSize", "en")
    screensize_txt  = " ".join(screensize_vals)

    combinado = " ".join(filter(lambda x: x != "--", [display, display_multi, screen, screensize_txt, todo]))

    tipo = "--"
    for t in ["DynamicAMOLED", "Super AMOLED", "AMOLED", "OLED", "PLS LCD", "LCD", "IPS", "TFT", "Retina"]:
        if t.lower() in combinado.lower():
            tipo = t.replace(" ", "")
            break

    # Tamaño en pulgadas: "3.1-inch", "5.0\"", "6.7 inches", o dbp:screen = 320 (pixels, no útil)
    pulgadas = "--"
    for patron in [
        r'(\d+\.?\d*)\s*[-–]?\s*(?:inch(?:es)?|")',
        r'display\s*[:\-]?\s*(\d+\.?\d*)',
        # ← NUEVO: "6.7 in" o "6.7in" sin "inches" completo
        r'(\d+\.?\d*)\s*in\b',
    ]:
        m = re.search(patron, combinado, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            if 2.0 <= val <= 8.0:  # rango realista para pantallas
                pulgadas = str(val)
                break

    # Resolución: "1920x1080", "320 × 480", o dbo:screenResolution
    res = "--"
    m = re.search(r'(\d{3,4})\s*[x×]\s*(\d{3,4})', combinado, re.IGNORECASE)
    if m:
        a, b = sorted([int(m.group(1)), int(m.group(2))])
        res = f"{a}x{b}"
    elif res_dbo != "--":
        # dbo:screenResolution puede ser "320" (solo ancho) o "320x480"
        m2 = re.search(r'(\d{3,4})[x×](\d{3,4})', res_dbo)
        if m2:
            a, b = sorted([int(m2.group(1)), int(m2.group(2))])
            res = f"{a}x{b}"

    hz = _num(combinado, r'(\d+)\s*hz')

    return {"tipo": tipo, "pulgadas": pulgadas, "hz": hz, "res": res}


def parsear_camara(props: dict, todo: str) -> dict:
    cam = _val(props, DBP + "camera")
    px_dbo = _val(props, DBO + "numberOfPixels")  # ← NUEVO: puede ser numérico
    # ← NUEVO: dbp:frontCamera suele tener solo el número en MP (ej: 5 → "5")
    front_cam_vals = _vals(props, DBP + "frontCamera")
    # ← NUEVO: recoger todos los valores de dbp:camera (puede venir en múltiples entradas)
    cam_vals = _vals(props, DBP + "camera", "en")
    if not cam_vals:
        cam_vals = _vals(props, DBP + "camera")
    cam_multi = " ".join(cam_vals)

    if cam == "--":
        cam = todo

    combinado = cam + " " + cam_multi + " " + todo

    mp_trasera = "--"
    # Patrón explícito: "50 MP rear", "12 megapixel", o solo "12 MP"
    for patron in [
        r'(\d+)\s*mp\s*(?:main|rear|back|primary|trasera)',
        r'(\d+)\s*megapixel',
        r'(\d+)\s*mp\b',
    ]:
        m = re.search(patron, combinado, re.IGNORECASE)
        if m:
            mp_trasera = m.group(1)
            break

    # Si dbo:numberOfPixels es numérico (ej: 5 = 5MP)
    if mp_trasera == "--" and px_dbo != "--":
        try:
            px = int(float(px_dbo))
            if 1 <= px <= 200:
                mp_trasera = str(px)
        except:
            pass

    mp_frontal = "--"
    # ← NUEVO: buscar primero en dbp:frontCamera (valor numérico directo, ej: "5")
    for fv in front_cam_vals:
        fv = fv.strip()
        try:
            px_f = int(float(fv))
            if 1 <= px_f <= 100:
                mp_frontal = str(px_f)
                break
        except:
            pass
    # Si no se encontró, buscar en texto combinado
    if mp_frontal == "--":
        m = re.search(r'(\d+)\s*mp\s*(?:front|selfie|frontal)', combinado, re.IGNORECASE)
        if m:
            mp_frontal = m.group(1)

    num_camaras = "--"
    for palabra, num in [("triple","3"),("quad","4"),("dual","2"),("single","1"),("penta","5")]:
        if palabra in combinado.lower():
            num_camaras = num
            break
    if num_camaras == "--":
        m2 = re.search(r'(\d)\s*(?:rear|back|main)?\s*camera', cam, re.IGNORECASE)
        if m2:
            num_camaras = m2.group(1)
    # ← NUEVO: fallback contando MP separados por coma (ej: "50 MP + 5 MP" → 2 cámaras)
    if num_camaras == "--":
        mp_list = re.findall(r'\d+\s*mp', combinado, re.IGNORECASE)
        # Descontar la cámara frontal si ya se detectó
        count = len(mp_list)
        if count >= 2 and mp_frontal != "--":
            count -= 1
        if count >= 1:
            num_camaras = str(count)

    return {"mp": mp_trasera, "num": num_camaras, "frontal": mp_frontal}


def parsear_memoria(props: dict, todo: str) -> dict:
    # DBpedia usa distintas propiedades según el modelo:
    # dbp:memory  → "RAM: 256MB, ROM: 512MB" o "2 GB RAM, 32 GB"
    # dbp:ram     → "2 GB" o "2048 MB"
    # dbp:storage → "32 GB" o "256 GB"
    # dbo:memory  → valor numérico en bytes

    ram_txt  = _val(props, DBP + "ram")
    stor_txt = _val(props, DBP + "storage")
    mem_txt  = _val(props, DBP + "memory")        # ← NUEVO: campo combinado
    mem_dbo  = _val(props, DBO + "memory")        # ← NUEVO: ontología DBO

    # También buscar en todos los valores sin filtro de idioma
    ram_vals  = _vals(props, DBP + "ram")
    stor_vals = _vals(props, DBP + "storage")
    mem_vals  = _vals(props, DBP + "memory")

    # ← NUEVO: dbp:storage a veces viene como entero concatenado de variantes
    # ej: "3264128" = 32+64+128 GB pegados. Detectar y tomar el menor valor típico.
    stor_vals_clean = []
    for sv in stor_vals:
        sv_strip = sv.strip()
        # Si es un número puro largo (>= 5 dígitos) sin unidad → probablemente concatenado
        if re.match(r'^\d{5,}$', sv_strip):
            # Intentar separar en bloques de tamaños típicos (32, 64, 128, 256, 512)
            SIZES = [512, 256, 128, 64, 32, 16, 8]
            resto = int(sv_strip)
            encontrados = []
            for s in SIZES:
                while resto % s == 0 and resto > 0:
                    # no aplicar: puede ser falso positivo. Mejor regex greedy
                    break
            # Alternativa: extraer todos los números de 2-3 dígitos típicos del string
            partes = re.findall(r'(512|256|128|64|32|16|8)(?=\d{2,}|\b)', sv_strip)
            if partes:
                stor_vals_clean.append(partes[0] + " GB")  # tomar el más pequeño disponible primero
            else:
                stor_vals_clean.append(sv)
        else:
            stor_vals_clean.append(sv)
    stor_vals = stor_vals_clean
    if stor_txt.strip() and re.match(r'^\d{5,}$', stor_txt.strip()):
        partes = re.findall(r'(512|256|128|64|32|16|8)(?=\d{2,}|\b)', stor_txt.strip())
        stor_txt = (partes[0] + " GB") if partes else stor_txt

    combinado = " ".join(filter(lambda x: x != "--", [
        ram_txt, stor_txt, mem_txt, mem_dbo,
        " ".join(ram_vals), " ".join(stor_vals), " ".join(mem_vals),
        todo
    ]))

    # ── RAM ──────────────────────────────────────────────────────────────────
    ram = "--"

    # Construir fuente SOLO para RAM (sin mezclar con storage para evitar confusión)
    combinado_ram = " ".join(filter(lambda x: x != "--" and x.strip(), [
        ram_txt, mem_txt, mem_dbo,
        " ".join(ram_vals), " ".join(mem_vals),
    ]))

    # Patrón 0 (más prioritario): entradas de dbp:memory con formato "Variantes: N GB, M GB"
    # ej: "A05/A05s/M14: 4 GB, 6 GB" → 4
    # Ejecutar ANTES de combinado para no confundir con storage
    for mv in _vals(props, DBP + "memory", "en") + _vals(props, DBP + "memory"):
        mv = mv.strip()
        # Ignorar líneas que son solo tipo de memoria (LPDDR4X, eMMC, NVMe, etc.)
        if re.match(r'^[A-Za-z]+[\dA-Za-z]*$', mv):
            continue
        # Patrón "Modelos: N GB" o "Modelos: N GB, M GB"
        m_var = re.search(r':\s*(\d+)\s*gb', mv, re.IGNORECASE)
        if m_var:
            val = int(m_var.group(1))
            if 1 <= val <= 32:      # RAM realista: máx 32 GB
                ram = str(val)
                break
        # Patrón simple: "N GB" solo (ej iPhone: dbp:memory = "12")
        m_solo = re.match(r'^(\d{1,2})(?:\s*gb)?$', mv, re.IGNORECASE)
        if m_solo:
            val = int(m_solo.group(1))
            if 1 <= val <= 32:
                ram = str(val)
                break

    # Patrón explícito con texto de RAM
    if ram == "--":
        for patron in [
            r'ram\s*[:\-]\s*(\d+)\s*(gb|mb)',
            r'(\d+)\s*(gb|mb)\s*(?:of\s*)?ram\b',
            r'(\d+)\s*(gb|mb)\s*(?:lpddr|ddr)\d*',
            r'\bram\b[^\d]{0,3}(\d+)\s*(gb|mb)',
        ]:
            m = re.search(patron, combinado_ram, re.IGNORECASE)
            if m:
                valor = int(m.group(1))
                unidad = m.group(2).lower()
                if unidad == "mb":
                    if valor >= 512:
                        gb_calc = round(valor / 1024)
                        ram = str(gb_calc) if gb_calc > 0 else "1"
                    else:
                        ram = f"{valor}MB"
                else:
                    if valor > 0:
                        ram = str(valor)
                break

    # Fallback: si ram_txt tiene solo un número de GB
    if ram == "--":
        m = re.search(r'^(\d+)\s*gb$', ram_txt.strip(), re.IGNORECASE)
        if m:
            ram = m.group(1)

    # Buscar en dbp:memory patrones como "3 or 4GB RAM", "4, 6 or 8GB RAM"
    if ram == "--" and mem_txt != "--":
        m_or = re.search(r'(\d+)\s*(?:or\s*\d+)*\s*(?:gb|mb)\s*ram', mem_txt, re.IGNORECASE)
        if m_or:
            ram = m_or.group(1)

    # Fallback numérico DBO (viene en bytes)
    if ram == "--" and mem_dbo != "--":
        try:
            bytes_val = float(mem_dbo)
            gb_val = round(bytes_val / (1024**3))
            if 1 <= gb_val <= 64:
                ram = str(gb_val)
        except:
            pass

    # ── ALMACENAMIENTO ───────────────────────────────────────────────────────
    stor = "--"

    # Patrón explícito: "ROM: 512MB" o "256GB ROM" o "64 GB storage"
    # NOTA: el orden importa — "(\d+) GB ROM" ANTES que "ROM (\d+)" para evitar
    # que "256 GB ROM 16 GB RAM" matchee 'ROM 16' en vez de '256 GB ROM'
    for patron in [
        r'(\d+)\s*(gb|mb)\s*(?:rom|flash|internal)',  # 256GB ROM / 256GB internal  ← movido arriba
        r'internal\s*(?:storage|memory)[:\s]+(\d+)\s*(gb|mb)',
        r'storage\s*[:\-]?\s*(\d+)\s*(gb|mb)',        # storage: 256GB
        r'rom\s*[:\-]\s*(\d+)\s*(gb|mb)',             # ROM: 512MB  (con separador explícito)
    ]:
        m = re.search(patron, combinado, re.IGNORECASE)
        if m:
            valor = int(m.group(1))
            unidad = m.group(2).lower()
            if unidad == "mb":
                if valor >= 512:
                    gb_calc = round(valor / 1024)
                    stor = str(gb_calc) if gb_calc > 0 else f"{valor}MB"
                else:
                    stor = f"{valor}MB"   # e.g. "256MB"
            else:
                stor = str(valor)
            break

    # Fallback: buscar GB típicos de almacenamiento en todo el texto
    # Pero solo si viene de propiedades de storage explícitas
    if stor == "--":
        # Intentar solo en stor_txt/mem_txt primero (evitar confusión con RAM)
        fuente_stor = " ".join(filter(lambda x: x != "--", [stor_txt, " ".join(stor_vals)]))
        if fuente_stor.strip():
            matches = re.findall(r'(\d+)\s*gb', fuente_stor, re.IGNORECASE)
            for v in matches:
                iv = int(v)
                if iv in (4, 8, 16, 32, 64, 128, 256, 512, 1024):
                    stor = v
                    break
        # Último fallback en texto completo (riesgo de confusión menor)
        if stor == "--":
            matches = re.findall(r'(\d+)\s*gb', combinado, re.IGNORECASE)
            for v in matches:
                iv = int(v)
                if iv in (32, 64, 128, 256, 512, 1024):  # Solo sizes típicos de storage
                    # Evitar confundir con RAM detectada
                    try:
                        ram_int = int(ram.replace("MB","").replace("GB","")) if ram not in ("--",) and ram[0].isdigit() else -1
                    except:
                        ram_int = -1
                    if iv != ram_int:
                        stor = v
                        break

    # ── MICRO SD ─────────────────────────────────────────────────────────────
    micro_sd = bool(re.search(r'micro\s*sd|expandable|memory\s*card|microsd\s*slot', combinado, re.IGNORECASE))
    if re.search(r'no\s+(?:micro|sd|expand)|not\s+expand|does\s+not\s+support.*(?:sd|expand)', combinado, re.IGNORECASE):
        micro_sd = False

    return {"ram": ram, "storage": stor, "micro_sd": micro_sd}

    # ── RAM ──────────────────────────────────────────────────────────────────
    ram = "--"

    # Patrón explícito: "RAM: 256MB", "2 GB RAM", "8GB LPDDR5"
    # Orden importa: los más específicos primero
    for patron in [
        r'ram\s*[:\-]\s*(\d+)\s*(gb|mb)',           # RAM: 256MB  / RAM: 2GB  (con separador)
        r'(\d+)\s*(gb|mb)\s*(?:of\s*)?ram\b',       # 2GB RAM / 256MB of RAM
        r'(\d+)\s*(gb|mb)\s*(?:lpddr|ddr)\d*',      # 8GB LPDDR5
        r'\bram\b[^\d]{0,5}(\d+)\s*(gb|mb)',        # RAM ... 8GB (hasta 5 chars de separación)
    ]:
        m = re.search(patron, combinado, re.IGNORECASE)
        if m:
            valor = int(m.group(1))
            unidad = m.group(2).lower()
            if unidad == "mb":
                if valor >= 512:
                    gb_calc = round(valor / 1024)
                    ram = str(gb_calc) if gb_calc > 0 else "1"
                else:
                    ram = f"{valor}MB"
            else:
                if valor > 0:
                    ram = str(valor)
            break

    # Fallback: si ram_txt tiene solo un número de GB
    if ram == "--":
        m = re.search(r'^(\d+)\s*gb$', ram_txt.strip(), re.IGNORECASE)
        if m:
            ram = m.group(1)

    # Fallback numérico DBO (viene en bytes)
    if ram == "--" and mem_dbo != "--":
        try:
            bytes_val = float(mem_dbo)
            gb_val = round(bytes_val / (1024**3))
            if 1 <= gb_val <= 64:
                ram = str(gb_val)
        except:
            pass

    # ── ALMACENAMIENTO ───────────────────────────────────────────────────────
    stor = "--"

    # Patrón explícito: "ROM: 512MB" o "ROM: 32GB" o "64 GB storage"
    for patron in [
        r'rom\s*[:\-]?\s*(\d+)\s*(gb|mb)',           # ROM: 512MB
        r'(\d+)\s*(gb|mb)\s*(?:rom|flash|internal)',  # 256GB internal
        r'internal\s*(?:storage|memory)[:\s]+(\d+)\s*(gb|mb)',
        r'storage\s*[:\-]?\s*(\d+)\s*(gb|mb)',        # storage: 256GB
    ]:
        m = re.search(patron, combinado, re.IGNORECASE)
        if m:
            valor = int(m.group(1))
            unidad = m.group(2).lower()
            if unidad == "mb":
                if valor >= 512:
                    gb_calc = round(valor / 1024)
                    stor = str(gb_calc) if gb_calc > 0 else f"{valor}MB"
                else:
                    stor = f"{valor}MB"   # e.g. "256MB"
            else:
                stor = str(valor)
            break

    # Fallback: buscar GB típicos de almacenamiento en todo el texto
    # Pero solo si viene de propiedades de storage explícitas
    if stor == "--":
        # Intentar solo en stor_txt/mem_txt primero (evitar confusión con RAM)
        fuente_stor = " ".join(filter(lambda x: x != "--", [stor_txt, " ".join(stor_vals)]))
        if fuente_stor.strip():
            matches = re.findall(r'(\d+)\s*gb', fuente_stor, re.IGNORECASE)
            for v in matches:
                iv = int(v)
                if iv in (4, 8, 16, 32, 64, 128, 256, 512, 1024):
                    stor = v
                    break
        # Último fallback en texto completo (riesgo de confusión menor)
        if stor == "--":
            matches = re.findall(r'(\d+)\s*gb', combinado, re.IGNORECASE)
            for v in matches:
                iv = int(v)
                if iv in (32, 64, 128, 256, 512, 1024):  # Solo sizes típicos de storage
                    # Evitar confundir con RAM detectada
                    try:
                        ram_int = int(ram.replace("MB","").replace("GB","")) if ram not in ("--",) and ram[0].isdigit() else -1
                    except:
                        ram_int = -1
                    if iv != ram_int:
                        stor = v
                        break

    # ← NUEVO: buscar storage en dbp:memory con variantes de modelo
    #   ej: "A05/A05s/M14: 64 GB, 128 GB" → tomar el primer valor
    if stor == "--":
        for mv in _vals(props, DBP + "memory", "en") + _vals(props, DBP + "memory"):
            mv = mv.strip()
            # Ignorar entradas de tipo de RAM (LPDDR4X etc.)
            if re.match(r'^[A-Z]+\d*[A-Z]*\d*$', mv):
                continue
            m_var = re.search(r':\s*(\d+)\s*gb', mv, re.IGNORECASE)
            if m_var:
                val = int(m_var.group(1))
                # Solo si es tamaño típico de storage (>= 32 GB) y distinto de la RAM detectada
                try:
                    ram_int = int(ram) if ram not in ("--",) and str(ram).isdigit() else -1
                except:
                    ram_int = -1
                if val in (32, 64, 128, 256, 512, 1024) and val != ram_int:
                    stor = str(val)
                    break

    # ← NUEVO: fallback para dbp:storage con valor numérico puro sin unidad
    #   ej: dbp:storage = "64" (Samsung A-series) o "128"/"256"/"512" (iPhone)
    SIZES_STORAGE = {8, 16, 32, 64, 128, 256, 512, 1024}
    if stor == "--":
        try:
            ram_int_fb = int(ram) if ram not in ("--",) and str(ram).isdigit() else -1
        except:
            ram_int_fb = -1
        # Caso A: un solo valor numérico puro (ej Samsung "64")
        for sv in stor_vals:
            sv = sv.strip()
            if re.match(r'^\d+$', sv):
                try:
                    iv = int(sv)
                    if iv in SIZES_STORAGE and iv != ram_int_fb:
                        stor = sv
                        break
                except:
                    pass
        # Caso B: múltiples variantes "128", "256", "512" → tomar el menor (iPhone)
        if stor == "--":
            candidatos = []
            for sv in stor_vals:
                sv_s = sv.strip()
                m_sv = re.match(r'^(\d+)\s*(?:gb)?$', sv_s, re.IGNORECASE)
                if m_sv:
                    iv = int(m_sv.group(1))
                    if iv in SIZES_STORAGE and iv != ram_int_fb:
                        candidatos.append(iv)
            if candidatos:
                stor = str(min(candidatos))

    # ── MICRO SD ─────────────────────────────────────────────────────────────
    micro_sd = bool(re.search(r'micro\s*sd|expandable|memory\s*card|microsd\s*slot', combinado, re.IGNORECASE))
    if re.search(r'no\s+(?:micro|sd|expand)|not\s+expand|does\s+not\s+support.*(?:sd|expand)', combinado, re.IGNORECASE):
        micro_sd = False

    return {"ram": ram, "storage": stor, "micro_sd": micro_sd}


def parsear_cpu(props: dict, todo: str) -> dict:
    cpu_txt = _val(props, DBP + "cpu")
    cpu_dbo = _val(props, DBO + "cpu")   # ← NUEVO: puede ser numérico (MHz)
    cpu_int = "--"

    # ← NUEVO: leer dbp:soc como URI (ej: dbr:Apple_A19, dbr:Snapdragon_8_Gen_3)
    soc_uris = _vals(props, DBP + "soc")
    soc_txt_extra = ""
    for soc_uri in soc_uris:
        # Puede ser URI o texto libre
        if "/" in soc_uri:
            # Es URI: extraer el nombre del recurso
            soc_nombre = soc_uri.split("/")[-1].replace("_", " ")
        else:
            soc_nombre = soc_uri
        soc_txt_extra += " " + soc_nombre

    # Si dbo:cpu es numérico (MHz), convertir a GHz
    if cpu_dbo != "--":
        try:
            mhz = float(cpu_dbo)
            if 100 <= mhz <= 5000:
                cpu_int = str(round(mhz / 1000, 2))  # MHz → GHz
        except:
            pass

    combinado = " ".join(filter(lambda x: x not in ("--", ""), [cpu_txt, soc_txt_extra, cpu_dbo if cpu_dbo.replace(".","").isdigit() == False else "", todo]))
    if combinado.strip() == "":
        combinado = todo

    marca  = "--"
    modelo = "--"
    nucleos = "--"
    ghz    = "--"

    # ← NUEVO: detectar Apple A-series desde URI del SOC (ej: "Apple A19", "Apple A18 Pro")
    for soc_uri in soc_uris:
        soc_nombre = soc_uri.split("/")[-1].replace("_", " ") if "/" in soc_uri else soc_uri
        m_apple = re.search(r'Apple\s+(A\d+\s*(?:Pro|Bionic|Fusion)?)', soc_nombre, re.IGNORECASE)
        if m_apple:
            marca = "Apple"
            modelo = f"Apple {m_apple.group(1).strip()}"
            break
        m_snap = re.search(r'Snapdragon\s+[\w\s]+', soc_nombre, re.IGNORECASE)
        if m_snap:
            marca = "Qualcomm"
            modelo = m_snap.group(0).strip()
            break
        m_dim = re.search(r'Dimensity\s+\d+', soc_nombre, re.IGNORECASE)
        if m_dim:
            marca = "MediaTek"
            modelo = m_dim.group(0).strip()
            break

    # Detección por texto (cpu_txt, combinado) si SOC URI no resolvió
    if marca == "--":
        for fuente in [cpu_txt, soc_txt_extra, combinado]:
            if fuente in ("--", ""):
                continue
            for m_cpu, patron in [
                ("Qualcomm",  r'(Snapdragon\s+(?:\d+\w*\s*)+(?:Gen\s*\d+)?)'),
                ("Apple",     r'(A\d+\s*\w+\s*Bionic|Apple\s*A\d+\s*\w*)'),
                ("MediaTek",  r'(Dimensity\s*\d+|Helio\s*\w+)'),
                ("Samsung",   r'(Exynos\s*\d+)'),
                ("Google",    r'(Tensor\s*G?\d*)'),
                ("HiSilicon", r'(Kirin\s*\d+)'),
                ("Qualcomm",  r'(MSM\s*\d+)'),
                ("Unisoc",    r'(Unisoc\s*\w+|Tiger\s*T\d+)'),
            ]:
                m = re.search(patron, fuente, re.IGNORECASE)
                if m:
                    marca  = m_cpu
                    modelo = m.group(1).strip()
                    break
            if marca != "--":
                break

    # ← CORREGIDO: agregar 6-core, 8s/8-core, penta y otros formatos numéricos
    # Para evitar que "dual SIM" o "dual band" cuenten como 2 núcleos,
    # buscar "dual" solo si aparece junto a "core" o en cpu_txt/soc
    fuente_nucleos = cpu_txt + " " + soc_txt_extra
    if fuente_nucleos.strip() in ("", " "):
        fuente_nucleos = combinado

    for palabra, num in [
        ("deca",    "10"),
        ("octa",    "8"),
        ("hexa",    "6"),
        ("6-core",  "6"),
        ("quad",    "4"),
        ("4-core",  "4"),
        ("dual",    "2"),
        ("penta",   "5"),
    ]:
        # Para "dual" requerir contexto de "core" o "cpu" para evitar falsos positivos
        if palabra == "dual":
            if re.search(r'dual[\s-]*core|dual[\s-]*cpu', combinado, re.IGNORECASE):
                nucleos = num
                break
        elif palabra in fuente_nucleos.lower() or palabra in combinado.lower():
            nucleos = num
            break
    # ← NUEVO: fallback numérico "8 cores", "6 cores"
    if nucleos == "--":
        m_cores = re.search(r'(\d+)\s*[-–]?\s*core', combinado, re.IGNORECASE)
        if m_cores:
            nucleos = m_cores.group(1)

    # Frecuencia: priorizar dbo:cpu numérico (MHz), luego texto
    if cpu_int != "--":
        ghz = cpu_int
    else:
        ghz = _num(combinado, r'(\d+\.?\d*)\s*ghz')
        if ghz == "--":
            # Buscar MHz explícito
            m_mhz = re.search(r'(\d{3,4})\s*mhz', combinado, re.IGNORECASE)
            if m_mhz:
                ghz = str(round(int(m_mhz.group(1)) / 1000, 2))

    return {"marca": marca, "modelo": modelo, "nucleos": nucleos, "ghz": ghz}


def parsear_conectividad(props: dict, todo: str) -> dict:
    conn_vals    = _vals(props, DBP + "connectivity", "en")
    network_vals = _vals(props, DBP + "networks", "en")
    net_dbo_vals = _vals(props, DBO + "networkType")

    # Para WiFi, BT, NFC: usar connectivity + todo el texto
    conn = " ".join(conn_vals) + " " + todo

    # Para red móvil: usar solo los campos específicos de red, sin todo el texto libre
    # (evita falsos positivos con menciones de otros modelos en el abstract)
    red_txt = " ".join(conn_vals + network_vals + net_dbo_vals)

    wifi = "--"
    if re.search(r'802\.11\s*\w*be|wi.?fi\s*7', conn, re.IGNORECASE):
        wifi = "WiFi7"
    elif re.search(r'802\.11\s*\w*ax|wi.?fi\s*6', conn, re.IGNORECASE):
        wifi = "WiFi6"
    elif re.search(r'802\.11\s*[abgn/]+|wi.?fi\s*(?:4|5|[abgn])', conn, re.IGNORECASE):
        wifi = "WiFi4"

    bt = "--"
    m = re.search(r'bluetooth\s*[v:]?\s*(\d+\.?\d*)', conn, re.IGNORECASE)
    if m:
        bt = m.group(1)

    nfc = bool(re.search(r'\bnfc\b', conn, re.IGNORECASE))

    red = "--"
    if re.search(r'\b5g\b', red_txt, re.IGNORECASE):
        red = "5G"
    elif re.search(r'\b4g\b|lte\b', red_txt, re.IGNORECASE):
        red = "4G"
    elif re.search(r'\b3g\b|umts|hspa|hsdpa|wcdma', red_txt, re.IGNORECASE):
        red = "3G"
    elif re.search(r'\b2g\b|gsm\b|edge\b|gprs\b', red_txt, re.IGNORECASE):
        red = "2G"

    return {"wifi": wifi, "bluetooth": bt, "nfc": nfc, "red": red}


def parsear_so(props: dict) -> str:
    # Primero intentar URIs de dbo:operatingSystem
    os_uris = _vals(props, DBO + "operatingSystem")
    for uri_os in os_uris:
        if "android" in uri_os.lower():
            return "Android"
        if "ios" in uri_os.lower() or "iphone" in uri_os.lower():
            return "iOS"
        if "harmony" in uri_os.lower():
            return "HarmonyOS"

    # Fallback: leer dbp:os como texto libre (ej: "iOS 26", "Android 15 with One UI")
    os_txts = _vals(props, DBP + "os", "en")
    if not os_txts:
        os_txts = _vals(props, DBP + "os")
    for txt in os_txts:
        t = txt.lower()
        if "ios" in t or "iphone" in t:
            return "iOS"
        if "android" in t:
            return "Android"
        if "harmony" in t:
            return "HarmonyOS"

    # Fallback: revisar el fabricante — Apple siempre usa iOS
    dev_uris = _vals(props, DBP + "developer") + _vals(props, DBO + "manufacturer")
    for uri in dev_uris:
        if "apple" in uri.lower():
            return "iOS"

    return "Android"


def parsear_resistencia(todo: str) -> str:
    m = re.search(r'(IP\d{2})', todo, re.IGNORECASE)
    return m.group(1).upper() if m else "--"


def parsear_audio(props: dict, todo: str) -> str:
    sound = _val(props, DBP + "sound")
    if sound == "--":
        sound = todo
    if re.search(r'stereo|dolby|dual\s*speaker', sound, re.IGNORECASE):
        return "Stereo"
    return "--"


def parsear_sim(props: dict, todo: str) -> str:
    sim_txt = _val(props, DBP + "sim")
    if sim_txt == "--":
        sim_txt = todo
    t = sim_txt.lower()
    if "esim" in t or "e-sim" in t:
        return "eSIM"
    if "dual" in t:
        return "DualSIM"
    if "single" in t:
        return "SingleSIM"
    return "--"


def parsear_precio(props: dict) -> str:
    precio = _val(props, DBP + "price")
    if precio == "--":
        return "--"
    m = re.search(r'(\d{2,4})', precio)
    return m.group(1) if m else "--"


def parsear_anio(props: dict) -> str:
    released = _vals(props, DBP + "released")
    if not released:
        released = _vals(props, DBO + "releaseDate")
    if not released:
        released = _vals(props, DBP + "releaseDate")   # ← NUEVO
    if not released:
        released = _vals(props, DBP + "introduced")    # ← NUEVO
    for v in released:
        m = re.search(r'(\d{4})', v)
        if m and 2000 <= int(m.group(1)) <= 2030:
            return m.group(1)

    # Buscar año en el abstract (texto libre)
    abstract = _val(props, DBO + "abstract", "en")
    if abstract != "--":
        m = re.search(r'(?:released?|launched?|announced?|introduced?)\s+(?:in\s+)?(\d{4})', abstract, re.IGNORECASE)
        if m and 2000 <= int(m.group(1)) <= 2030:
            return m.group(1)

    return "--"


def parsear_marca(props: dict, recurso: str) -> str:
    MARCAS = ["Samsung","Apple","Google","Xiaomi","OnePlus","Oppo","Sony",
              "Motorola","Realme","Nothing","Huawei","Vivo","Nokia"]

    for uri_m in _vals(props, DBO + "manufacturer"):
        nombre = uri_m.split("/")[-1].replace("_", " ")
        for marca in MARCAS:
            if marca.lower() in nombre.lower():
                return marca

    for txt in _vals(props, DBP + "manufacturer", "en") + _vals(props, DBP + "manufacturer"):
        for marca in MARCAS:
            if marca.lower() in txt.lower():
                return marca

    for marca in MARCAS:
        if marca.lower() in recurso.lower():
            return marca

    if 'pixel' in recurso.lower():
        return "Google"
    if 'iphone' in recurso.lower():
        return "Apple"

    return "--"


def parsear_gama(precio_str: str, marca: str = "--", modelo: str = "--") -> str:
    if precio_str != "--":
        try:
            p = int(precio_str)
            if p >= 800:
                return "Alta"
            if p >= 400:
                return "Media"
            return "Baja"
        except:
            pass
    return "--"


def parsear_modelo(props: dict, recurso: str) -> str:
    nombres = _vals(props, FOAF_NAME, "en")
    if nombres:
        return sorted(nombres, key=len)[0]
    return recurso.replace("_", " ")


def _inferir_sensores(gama: str) -> list:
    return []


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def extraer_desde_dbpedia(recurso: str) -> dict:
    props = fetch_dbpedia_sparql(recurso)
    if not props:
        print(f"    ⚠  Sin datos para {recurso}")
        return {}

    todo = _todo_texto(props)

    pantalla = parsear_pantalla(props, todo)
    camara   = parsear_camara(props, todo)
    memoria  = parsear_memoria(props, todo)
    cpu      = parsear_cpu(props, todo)
    conn     = parsear_conectividad(props, todo)
    anio     = parsear_anio(props)
    precio   = parsear_precio(props)
    marca    = parsear_marca(props, recurso)
    modelo   = parsear_modelo(props, recurso)
    gama     = parsear_gama(precio, marca, modelo)

    datos = {
        "marca":             marca,
        "modelo":            modelo,
        "anio":              anio,
        "gama":              gama,
        "precio":            precio,
        "bateria_mah":       parsear_bateria_mah(props, todo),
        "carga_rapida_w":    parsear_carga_w(props, todo),
        "carga_inalambrica": parsear_carga_inalambrica(props, todo),
        "pantalla_tipo":     pantalla["tipo"],
        "pantalla_pulgadas": pantalla["pulgadas"],
        "pantalla_res":      pantalla["res"],
        "pantalla_hz":       pantalla["hz"],
        "camara_trasera_mp": camara["mp"],
        "camara_num":        camara["num"],
        "camara_frontal_mp": camara["frontal"],
        "ram_gb":            memoria["ram"],
        "storage_gb":        memoria["storage"],
        "micro_sd":          memoria["micro_sd"],
        "cpu_marca":         cpu["marca"],
        "cpu_modelo":        cpu["modelo"],
        "cpu_nucleos":       cpu["nucleos"],
        "cpu_ghz":           cpu["ghz"],
        "red_movil":         conn["red"],
        "wifi":              conn["wifi"],
        "bluetooth":         conn["bluetooth"],
        "nfc":               conn["nfc"],
        "so":                parsear_so(props),
        "resistencia":       parsear_resistencia(todo),
        "audio":             parsear_audio(props, todo),
        "sim":               parsear_sim(props, todo),
        "sensores":          _inferir_sensores(gama),
        "abstract_en":       _val(props, DBO + "abstract", "en")[:250],
        "abstract_es":       _val(props, DBO + "abstract", "es")[:250],
        "abstract_pt":       _val(props, DBO + "abstract", "pt")[:250],
    }

    _ABSTRACTS = ("abstract_en", "abstract_es", "abstract_pt")
    encontrados = [k for k, v in datos.items()
                   if v not in ("--", False, [], "") and k not in _ABSTRACTS]
    faltantes   = [k for k, v in datos.items()
                   if v == "--" and k not in _ABSTRACTS]
    print(f"    ✅ Encontrados ({len(encontrados)}): {', '.join(encontrados)}")
    if faltantes:
        print(f"    ⚠  Sin datos  ({len(faltantes)}): {', '.join(faltantes)}")

    return datos


# ═══════════════════════════════════════════════════════════════════════════════
# POBLADOR DEL GRAFO RDF
# ═══════════════════════════════════════════════════════════════════════════════

def rdf_uri(nombre: str) -> URIRef:
    return URIRef(NS_URI + nombre)

def _id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", s).strip("_")

def _lit_int(v: str) -> Literal:
    return Literal(int(v), datatype=XSD.integer)

def _lit_float(v: str) -> Literal:
    return Literal(float(v), datatype=XSD.float)


class Poblador:
    def __init__(self, g: Graph):
        self.g = g
        self._existentes = {str(s) for s in g.subjects(RDF.type, None)}

    def existe(self, nombre: str) -> bool:
        return NS_URI + nombre in self._existentes

    def add(self, s, p, o):
        self.g.add((s, p, o))

    def _reg(self, nombre: str):
        self._existentes.add(NS_URI + nombre)

    def asegurar_bateria(self, mah: str, carga_w: str, inalam: bool) -> str:
        nombre = f"Bateria_{mah}" if mah != "--" else "Bateria_Desconocida"
        if not self.existe(nombre):
            b = rdf_uri(nombre)
            self.add(b, RDF.type, OWL.NamedIndividual)
            self.add(b, RDF.type, NS.Bateria)
            if mah != "--":
                self.add(b, NS.capacidad, _lit_int(mah))
            if carga_w != "--":
                self.add(b, NS.cargaRapida, _lit_int(carga_w))
            self.add(b, NS.cargaInalambrica, Literal(inalam, datatype=XSD.boolean))
            self._reg(nombre)
            print(f"      + Bateria: {nombre}")
        return nombre

    def asegurar_pantalla(self, tipo: str, pulgadas: str, res: str, hz: str) -> str:
        t_id  = _id(tipo)     if tipo     != "--" else "XX"
        p_id  = pulgadas.replace(".", "") if pulgadas != "--" else "XX"
        h_id  = hz            if hz       != "--" else "XX"
        nombre = f"Pantalla_{t_id}_{p_id}_{h_id}"
        if not self.existe(nombre):
            p = rdf_uri(nombre)
            self.add(p, RDF.type, OWL.NamedIndividual)
            self.add(p, RDF.type, NS.Pantalla)
            self.add(p, NS.tipoPantalla, Literal(tipo if tipo != "--" else "Desconocido"))
            if pulgadas != "--":
                self.add(p, NS.tamanoPantalla, _lit_float(pulgadas))
            if res != "--":
                self.add(p, NS.resolucionPantalla, Literal(res))
            if hz != "--":
                self.add(p, NS.tasaRefresco, _lit_int(hz))
            self._reg(nombre)
            print(f"      + Pantalla: {nombre}")
        return nombre

    def asegurar_procesador(self, marca: str, modelo: str, nucleos: str, ghz: str) -> str:
        m_id   = _id(modelo)[:50] if modelo != "--" else "Desconocido"
        nombre = f"CPU_{m_id}"
        if not self.existe(nombre):
            p = rdf_uri(nombre)
            self.add(p, RDF.type, OWL.NamedIndividual)
            self.add(p, RDF.type, NS.Procesador)
            self.add(p, NS.marcaCPU,  Literal(marca  if marca  != "--" else "Desconocida"))
            self.add(p, NS.modeloCPU, Literal(modelo if modelo != "--" else "Desconocido"))
            if nucleos != "--":
                self.add(p, NS.numeroNucleos,   _lit_int(nucleos))
            if ghz != "--":
                self.add(p, NS.frecuenciaMaxima, _lit_float(ghz))
            self._reg(nombre)
            print(f"      + Procesador: {nombre}")
        return nombre

    def asegurar_memoria(self, ram: str, storage: str, micro_sd: bool) -> str:
        r_id = ram     if ram     != "--" else "X"
        s_id = storage if storage != "--" else "X"
        # Limpiar para usar como ID (ej: "256MB" → "256MB", "8" → "8")
        r_id_safe = re.sub(r"[^A-Za-z0-9]", "", r_id)
        s_id_safe = re.sub(r"[^A-Za-z0-9]", "", s_id)
        nombre = f"Memoria_{r_id_safe}_{s_id_safe}"
        if not self.existe(nombre):
            m = rdf_uri(nombre)
            self.add(m, RDF.type, OWL.NamedIndividual)
            self.add(m, RDF.type, NS.Memoria)
            # RAM: puede ser "8" (GB) o "256MB"
            if ram != "--":
                if ram.endswith("MB"):
                    try:
                        mb_val = int(ram[:-2])
                        # Guardar en MB como float en GB para consistencia
                        self.add(m, NS.RAM, Literal(round(mb_val / 1024, 3), datatype=XSD.float))
                    except:
                        self.add(m, NS.RAM, Literal(ram))
                else:
                    self.add(m, NS.RAM, _lit_int(ram))
            # Storage: puede ser "256" (GB) o "512MB"
            if storage != "--":
                if storage.endswith("MB"):
                    try:
                        mb_val = int(storage[:-2])
                        self.add(m, NS.almacenamientoInterno, Literal(round(mb_val / 1024, 3), datatype=XSD.float))
                    except:
                        self.add(m, NS.almacenamientoInterno, Literal(storage))
                else:
                    self.add(m, NS.almacenamientoInterno, _lit_int(storage))
            self.add(m, NS.admiteMicroSD, Literal(micro_sd, datatype=XSD.boolean))
            self._reg(nombre)
            print(f"      + Memoria: {nombre}")
        return nombre

    def asegurar_camara_trasera(self, mp: str, num: str) -> str:
        nombre = f"CamTrasera_{mp}MP_N{num}"
        if not self.existe(nombre):
            c = rdf_uri(nombre)
            self.add(c, RDF.type, OWL.NamedIndividual)
            self.add(c, RDF.type, NS.CamaraTrasera)
            if mp  != "--": self.add(c, NS.resolucionPrincipal, _lit_int(mp))
            if num != "--": self.add(c, NS.numeroCamaras,       _lit_int(num))
            self._reg(nombre)
            print(f"      + CamaraTrasera: {nombre}")
        return nombre

    def asegurar_camara_frontal(self, mp: str) -> str:
        nombre = f"CamFrontal_{mp}MP_DBpedia"
        if not self.existe(nombre):
            c = rdf_uri(nombre)
            self.add(c, RDF.type, OWL.NamedIndividual)
            self.add(c, RDF.type, NS.CamaraFrontal)
            if mp != "--": self.add(c, NS.resolucionFrontal, _lit_int(mp))
            self._reg(nombre)
            print(f"      + CamaraFrontal: {nombre}")
        return nombre

    def asegurar_resistencia(self, cert: str) -> str | None:
        if not cert or cert == "--":
            return None
        nombre = f"Res_{cert.replace('-','')}"
        if not self.existe(nombre):
            r = rdf_uri(nombre)
            self.add(r, RDF.type, OWL.NamedIndividual)
            self.add(r, NS.certificacion, Literal(cert))
            self._reg(nombre)
            print(f"      + Resistencia: {nombre}")
        return nombre

    def agregar_celular(self, nombre_local: str, datos: dict) -> bool:
        if self.existe(nombre_local):
            print(f"  ↩  {nombre_local} ya existe — omitido")
            return False

        bat_id   = self.asegurar_bateria(datos["bateria_mah"], datos["carga_rapida_w"], datos["carga_inalambrica"])
        pan_id   = self.asegurar_pantalla(datos["pantalla_tipo"], datos["pantalla_pulgadas"], datos["pantalla_res"], datos["pantalla_hz"])
        cpu_id   = self.asegurar_procesador(datos["cpu_marca"], datos["cpu_modelo"], datos["cpu_nucleos"], datos["cpu_ghz"])
        mem_id   = self.asegurar_memoria(datos["ram_gb"], datos["storage_gb"], datos["micro_sd"])
        cam_t_id = self.asegurar_camara_trasera(datos["camara_trasera_mp"], datos["camara_num"])
        cam_f_id = self.asegurar_camara_frontal(datos["camara_frontal_mp"])
        res_id   = self.asegurar_resistencia(datos["resistencia"])

        cel = rdf_uri(nombre_local)
        self.add(cel, RDF.type, OWL.NamedIndividual)
        self.add(cel, RDF.type, NS.Celular)

        self.add(cel, NS.marcaCelular,  Literal(datos["marca"]))
        self.add(cel, NS.modeloCelular, Literal(datos["modelo"]))
        if datos["anio"] != "--":
            self.add(cel, NS.anio, _lit_int(datos["anio"]))
        if datos["gama"] != "--":
            self.add(cel, NS.gama, Literal(datos["gama"]))
        if datos["precio"] != "--":
            self.add(cel, NS.precio, _lit_int(datos["precio"]))

        self.add(cel, NS.tieneBateria,       rdf_uri(bat_id))
        self.add(cel, NS.tienePantalla,      rdf_uri(pan_id))
        self.add(cel, NS.tieneProcesador,    rdf_uri(cpu_id))
        self.add(cel, NS.tieneMemoria,       rdf_uri(mem_id))
        self.add(cel, NS.tieneCamaraTrasera, rdf_uri(cam_t_id))
        self.add(cel, NS.tieneCamaraFrontal, rdf_uri(cam_f_id))

        MAP_RED  = {"5G":"Red_5G","4G":"Red_4G","3G":"Red_3G","2G":"Red_2G"}
        MAP_WIFI = {"WiFi7":"WiFi7","WiFi6":"WiFi6","WiFi4":"WiFi4"}

        if datos["red_movil"] in MAP_RED:
            self.add(cel, NS.tieneRedMovil, rdf_uri(MAP_RED[datos["red_movil"]]))
        if datos["wifi"] in MAP_WIFI:
            self.add(cel, NS.tieneRedInalambrica, rdf_uri(MAP_WIFI[datos["wifi"]]))

        # Bluetooth: crear nodo dinámico con la versión real de DBpedia
        bt_ver = datos.get("bluetooth", "--")
        if bt_ver != "--":
            bt_id = "Bluetooth_" + re.sub(r"[^A-Za-z0-9]", "_", bt_ver)
            bt_uri = rdf_uri(bt_id)
            if not self.existe(bt_id):
                self.add(bt_uri, RDF.type, OWL.NamedIndividual)
                self.add(bt_uri, RDF.type, NS.RedInalambrica)
                self.add(bt_uri, NS.tipoRedInalambrica, Literal(f"Bluetooth {bt_ver}"))
                self._reg(bt_id)
                print(f"      + Bluetooth: {bt_id}")
            self.add(cel, NS.tieneRedInalambrica, bt_uri)

        if datos["nfc"]:
            self.add(cel, NS.tieneRedInalambrica, rdf_uri("NFC"))

        MAP_SO = {"Android":"Android","iOS":"iOS","HarmonyOS":"HarmonyOS"}
        if datos["so"] in MAP_SO:
            self.add(cel, NS.tieneSistemaOperativo, rdf_uri(MAP_SO[datos["so"]]))

        MAP_SIM = {"DualSIM":"DualSIM","SingleSIM":"SingleSIM","eSIM":"eSIM"}
        if datos["sim"] in MAP_SIM:
            self.add(cel, NS.tieneTipoSIM, rdf_uri(MAP_SIM[datos["sim"]]))

        if datos["audio"] == "Stereo":
            self.add(cel, NS.tieneAudio, rdf_uri("AudioStereo"))
        elif datos["audio"] == "Mono":
            self.add(cel, NS.tieneAudio, rdf_uri("AudioMono"))

        MAP_SEN = {"huella":"SensorHuella","facial":"SensorFacial",
                   "giroscopio":"SensorGiroscopio","luz":"SensorLuz","proximidad":"SensorProximidad"}
        for s in datos.get("sensores", []):
            if s in MAP_SEN:
                self.add(cel, NS.tieneSensor, rdf_uri(MAP_SEN[s]))

        if res_id:
            self.add(cel, NS.tieneResistencia, rdf_uri(res_id))

        self.add(rdf_uri(bat_id),   NS.esBateriaDe,      cel)
        self.add(rdf_uri(pan_id),   NS.esPantallaDe,      cel)
        self.add(rdf_uri(cpu_id),   NS.esProcesadorDe,    cel)
        self.add(rdf_uri(mem_id),   NS.esMemoriaDe,       cel)
        self.add(rdf_uri(cam_t_id), NS.esCamaraTraseraDe, cel)
        self.add(rdf_uri(cam_f_id), NS.esCamaraFrontalDe, cel)

        for lang_key, lang_code in [("abstract_en", "en"), ("abstract_es", "es"), ("abstract_pt", "pt")]:
            texto = datos.get(lang_key, "--")
            if texto and texto != "--":
                self.add(cel, RDFS.comment, Literal(texto, lang=lang_code))

        self._reg(nombre_local)
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    entrada = Path(ONTOLOGIA_ENTRADA)
    if not entrada.exists():
        print(f"❌ No se encontró '{ONTOLOGIA_ENTRADA}'. Ejecutá en la carpeta del proyecto.")
        sys.exit(1)

    print("=" * 62)
    print("  POBLADOR AUTOMÁTICO v4 — SPARQL + XML (sin JSON)")
    print("=" * 62)
    print(f"\n📂 Cargando: {ONTOLOGIA_ENTRADA}")
    g = Graph()
    g.parse(str(entrada), format="xml")
    g.bind("", NS)
    tripletas_orig = len(g)
    print(f"   → {tripletas_orig} tripletas cargadas\n")

    poblador  = Poblador(g)
    agregados = 0
    omitidos  = []

    for nombre_local, recurso_db in CELULARES_OBJETIVO.items():
        print(f"\n📱 {nombre_local}  →  dbr:{recurso_db}")
        datos = extraer_desde_dbpedia(recurso_db)
        time.sleep(0.8)

        campos_clave = ["bateria_mah", "pantalla_pulgadas", "ram_gb", "anio",
                        "cpu_modelo", "red_movil", "camara_num", "bluetooth"]
        tiene_datos = sum(1 for c in campos_clave if datos.get(c, "--") != "--") >= 1

        if not datos or not tiene_datos:
            print(f"  ⚠  Datos insuficientes — omitido")
            omitidos.append(nombre_local)
            continue

        if poblador.agregar_celular(nombre_local, datos):
            agregados += 1
            print(f"  ✅ Celular agregado")

    salida = Path(ONTOLOGIA_SALIDA)
    g.serialize(destination=str(salida), format="xml")

    nuevas = len(g) - tripletas_orig
    print("\n" + "=" * 62)
    print(f"✅ ¡Poblado completado!")
    print(f"   Celulares agregados   : {agregados}")
    print(f"   Omitidos (sin datos)  : {len(omitidos)}")
    for o in omitidos:
        print(f"     - {o}")
    print(f"   Tripletas nuevas      : {nuevas}")
    print(f"   Total tripletas       : {len(g)}")
    print(f"   Archivo generado      : {ONTOLOGIA_SALIDA}")
    print("=" * 62)


if __name__ == "__main__":
    main()