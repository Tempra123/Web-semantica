"""
nlp.py
------
Motor de lenguaje natural para traducir texto libre en filtros SPARQL.

MEJORAS v2:
  - Precios: si el usuario pide "precio 300" y no hay celulares a ese precio exacto,
    el motor NO devuelve precio_max=300, sino que activa "modo proximidad":
    se busca el precio real más cercano >= al pedido y se devuelve precio_min=ese_valor.
    Así "precio 100" → precio_min=200 (el mínimo real), ordenado ASC.
    Y "precio 300" → precio_min=450 (el inmediato superior real).
  - Mismo patrón para batería exacta, RAM exacta, almacenamiento exacta, refresco.
  - Nuevo campo en filtros: "precio_modo" = "rango" | "maximo" | "minimo" | None
    para que sparql_engine ordene correctamente.
  - _extraer_numericos ahora maneja también "de 300 para arriba", "desde 300" como min.

Componentes:
  - VOCAB_SEMANTICO   : diccionario frase → (categoría, valor, positivo)
  - PALABRAS_RUIDO    : tokens a ignorar en búsqueda libre
  - PREFIJOS_NEGACION : prefijos que invierten el significado de un término
  - PRECIOS_REALES    : lista de precios presentes en la ontología (para snap)
  - interpretar_consulta(texto) → dict de filtros detectados
  - _aplicar_filtro(filtros, cat, val, negado) → bool
  - snap_al_precio_real(valor) → int (precio real más cercano hacia arriba)
"""

import re
from difflib import SequenceMatcher

# ═══════════════════════════════════════════════════════════════════════════════
# PRECIOS REALES DE LA ONTOLOGÍA  (actualizar si se agregan celulares)
# ═══════════════════════════════════════════════════════════════════════════════
PRECIOS_REALES: list[int] = sorted([
    200, 250, 250, 280, 450, 450, 450,
    500, 500, 650, 750, 750, 850, 850,
    1000, 1100, 1200, 1400,
])
_PRECIOS_UNICOS: list[int] = sorted(set(PRECIOS_REALES))

# Valores reales de RAM (GB)
_RAM_UNICOS: list[int] = [4, 6, 8, 12, 16]

# Valores reales de almacenamiento interno (GB)
_STORAGE_UNICOS: list[int] = [64, 128, 256, 512, 1024]

# Valores reales de batería (mAh)
_BATERIA_UNICOS: list[int] = [3000, 3700, 4000, 4300, 4500, 4800, 5000, 5200, 5500, 6000]

# Tamaños reales de pantalla (décimas de pulgada, i.e. 65 = 6.5")
_PANTALLA_UNICOS: list[int] = [62, 65, 67, 68, 69]

# Resoluciones reales de cámara trasera (MP)
_CAMARA_TRASERA_UNICOS: list[int] = [12, 48, 50, 64, 200]

# Resoluciones reales de cámara frontal (MP)
_CAMARA_FRONTAL_UNICOS: list[int] = [8, 12, 13, 16, 32]

# Tasas de refresco reales (Hz)
_REFRESCO_UNICOS: list[int] = [60, 90, 120]


def _snap_superior(valor: int, lista: list[int]) -> int | None:
    """Retorna el valor real más cercano >= valor, o None si no existe."""
    for v in lista:
        if v >= valor:
            return v
    return None


def _snap_inferior(valor: int, lista: list[int]) -> int | None:
    """Retorna el valor real más cercano <= valor, o None si no existe."""
    for v in reversed(lista):
        if v <= valor:
            return v
    return None


def snap_al_precio_real(valor: int) -> int | None:
    """
    Dado un precio pedido, retorna el precio real más cercano ≥ valor.
    Si el usuario pide 100 → retorna 200 (el mínimo real).
    Si pide 300 → retorna 450 (el siguiente precio real).
    Si pide 1500 → retorna None (por encima de todo).
    """
    return _snap_superior(valor, _PRECIOS_UNICOS)


# ═══════════════════════════════════════════════════════════════════════════════
# VOCABULARIO SEMÁNTICO
# ═══════════════════════════════════════════════════════════════════════════════
VOCAB_SEMANTICO: dict[str, tuple[str, str, bool]] = {

    # ── GAMA ──────────────────────────────────────────────────────────────────
    "gama alta":        ("gama", "Alta",  True),
    "gama media":       ("gama", "Media", True),
    "gama baja":        ("gama", "Baja",  True),
    "alta gama":        ("gama", "Alta",  True),
    "media gama":       ("gama", "Media", True),
    "baja gama":        ("gama", "Baja",  True),
    "high end":         ("gama", "Alta",  True),
    "flagship":         ("gama", "Alta",  True),
    "premium":          ("gama", "Alta",  True),
    "economico":        ("gama", "Baja",  True),
    "economica":        ("gama", "Baja",  True),
    "económico":        ("gama", "Baja",  True),
    "económica":        ("gama", "Baja",  True),
    "barato":           ("gama", "Baja",  True),
    "baratos":          ("gama", "Baja",  True),
    "asequible":        ("gama", "Baja",  True),
    "bajo costo":       ("gama", "Baja",  True),
    "bajo precio":      ("gama", "Baja",  True),
    "precio bajo":      ("gama", "Baja",  True),
    "caro":             ("gama", "Alta",  True),
    "caros":            ("gama", "Alta",  True),

    # ── SISTEMA OPERATIVO ─────────────────────────────────────────────────────
    "android":          ("so", "Android",   True),
    "ios":              ("so", "iOS",       True),
    "apple":            ("marca", "Apple",  True),
    "iphone":           ("marca", "Apple",  True),
    "harmonyos":        ("so", "HarmonyOS", True),
    "harmony":          ("so", "HarmonyOS", True),
    "harmony os":       ("so", "HarmonyOS", True),

    # ── MARCA ─────────────────────────────────────────────────────────────────
    "samsung":          ("marca", "Samsung",  True),
    "xiaomi":           ("marca", "Xiaomi",   True),
    "redmi":            ("marca", "Xiaomi",   True),
    "motorola":         ("marca", "Motorola", True),
    "moto":             ("marca", "Motorola", True),
    "huawei":           ("marca", "Huawei",   True),
    "oneplus":          ("marca", "OnePlus",  True),
    "one plus":         ("marca", "OnePlus",  True),
    "oppo":             ("marca", "Oppo",     True),
    "realme":           ("marca", "Realme",   True),
    "vivo":             ("marca", "Vivo",     True),

    # ── PROCESADOR — fabricante ────────────────────────────────────────────────
    "qualcomm":         ("cpu", "Qualcomm", True),
    "snapdragon":       ("cpu", "Qualcomm", True),
    "mediatek":         ("cpu", "MediaTek", True),
    "dimensity":        ("cpu", "MediaTek", True),
    "helio":            ("cpu", "MediaTek", True),
    "exynos":           ("cpu", "Samsung",  True),
    "kirin":            ("cpu", "Huawei",   True),
    "bionic":           ("cpu", "Apple",    True),

    # ── PROCESADOR — núcleos ──────────────────────────────────────────────────
    "octa core":        ("nucleos", "8", True),
    "8 nucleos":        ("nucleos", "8", True),
    "hexa core":        ("nucleos", "6", True),
    "6 nucleos":        ("nucleos", "6", True),

    # ── RAM (GB) ───────────────────────────────────────────────────────────────
    "4gb ram":          ("ram", "4",  True),
    "4 gb ram":         ("ram", "4",  True),
    "4 de ram":         ("ram", "4",  True),
    "4gb de ram":       ("ram", "4",  True),
    "6gb ram":          ("ram", "6",  True),
    "6 gb ram":         ("ram", "6",  True),
    "6gb de ram":       ("ram", "6",  True),
    "8gb ram":          ("ram", "8",  True),
    "8 gb ram":         ("ram", "8",  True),
    "8gb de ram":       ("ram", "8",  True),
    "12gb ram":         ("ram", "12", True),
    "12 gb ram":        ("ram", "12", True),
    "12gb de ram":      ("ram", "12", True),
    "16gb ram":         ("ram", "16", True),
    "16 gb ram":        ("ram", "16", True),
    "16gb de ram":      ("ram", "16", True),
    "mucha ram":        ("ram_min", "12",  True),
    "bastante ram":     ("ram_min", "8",   True),
    "poca ram":         ("ram_max", "6",   True),
    "ram 4":            ("ram", "4",  True),
    "ram 6":            ("ram", "6",  True),
    "ram 8":            ("ram", "8",  True),
    "ram 12":           ("ram", "12", True),
    "ram 16":           ("ram", "16", True),
    "memoria ram 4":    ("ram", "4",  True),
    "memoria ram 6":    ("ram", "6",  True),
    "memoria ram 8":    ("ram", "8",  True),
    "memoria ram 12":   ("ram", "12", True),

    # ── ALMACENAMIENTO ────────────────────────────────────────────────────────
    "64gb":             ("almacenamiento", "64",   True),
    "128gb":            ("almacenamiento", "128",  True),
    "256gb":            ("almacenamiento", "256",  True),
    "512gb":            ("almacenamiento", "512",  True),
    "1tb":              ("almacenamiento", "1024", True),
    "64 gb":            ("almacenamiento", "64",   True),
    "128 gb":           ("almacenamiento", "128",  True),
    "256 gb":           ("almacenamiento", "256",  True),
    "512 gb":           ("almacenamiento", "512",  True),
    "almacenamiento 64":    ("almacenamiento", "64",   True),
    "almacenamiento 128":   ("almacenamiento", "128",  True),
    "almacenamiento 256":   ("almacenamiento", "256",  True),
    "almacenamiento 512":   ("almacenamiento", "512",  True),
    "almacenamiento 1024":  ("almacenamiento", "1024", True),
    "mucho almacenamiento": ("almacenamiento", "256",  True),
    "poco almacenamiento":  ("almacenamiento", "64",   True),
    "memoria interna 64":   ("almacenamiento", "64",   True),
    "memoria interna 128":  ("almacenamiento", "128",  True),
    "memoria interna 256":  ("almacenamiento", "256",  True),
    "memoria interna 512":  ("almacenamiento", "512",  True),
    "espacio 128":          ("almacenamiento", "128",  True),
    "espacio 256":          ("almacenamiento", "256",  True),

    # ── MICRO-SD ──────────────────────────────────────────────────────────────
    "microsd":              ("microsd", "true",  True),
    "tarjeta sd":           ("microsd", "true",  True),
    "memoria expandible":   ("microsd", "true",  True),
    "sin microsd":          ("microsd", "false", True),
    "sin tarjeta sd":       ("microsd", "false", True),

    # ── PANTALLA — tipo ───────────────────────────────────────────────────────
    "amoled":           ("pantalla", "AMOLED",         True),
    "dynamic amoled":   ("pantalla", "Dynamic AMOLED", True),
    "oled":             ("pantalla", "OLED",           True),
    "lcd":              ("pantalla", "LCD",            True),

    # ── PANTALLA — tamaño ─────────────────────────────────────────────────────
    "pantalla grande":  ("pantalla_min", "68", True),
    "pantalla pequeña": ("pantalla_max", "62", True),
    "pantalla chica":   ("pantalla_max", "62", True),

    # ── PANTALLA — tasa refresco ──────────────────────────────────────────────
    "120hz":                    ("refresco", "120",     True),
    "120 hz":                   ("refresco", "120",     True),
    "90hz":                     ("refresco", "90",      True),
    "90 hz":                    ("refresco", "90",      True),
    "60hz":                     ("refresco", "60",      True),
    "60 hz":                    ("refresco", "60",      True),
    "alta tasa de refresco":    ("refresco_min", "90",  True),
    "buen refresco":            ("refresco_min", "90",  True),

    # ── BATERÍA — capacidad ───────────────────────────────────────────────────
    "bateria grande":   ("bateria_min", "5000", True),
    "buena bateria":    ("bateria_min", "4500", True),
    "batería grande":   ("bateria_min", "5000", True),
    "buena batería":    ("bateria_min", "4500", True),
    "mucha bateria":    ("bateria_min", "5000", True),
    "mucha batería":    ("bateria_min", "5000", True),
    "poca bateria":     ("bateria_max", "4000", True),
    "poca batería":     ("bateria_max", "4000", True),
    "5000mah":          ("bateria_min", "5000", True),
    "5000 mah":         ("bateria_min", "5000", True),
    "4000mah":          ("bateria_min", "4000", True),
    "4000 mah":         ("bateria_min", "4000", True),
    "capacidad 5000":   ("bateria_min", "5000", True),
    "capacidad 4500":   ("bateria_min", "4500", True),
    "capacidad 4000":   ("bateria_min", "4000", True),
    "capacidad 3000":   ("bateria_min", "3000", True),
    "bateria 5000":     ("bateria_min", "5000", True),
    "bateria 4500":     ("bateria_min", "4500", True),
    "bateria 4000":     ("bateria_min", "4000", True),
    "batería 5000":     ("bateria_min", "5000", True),
    "batería 4500":     ("bateria_min", "4500", True),
    "batería 4000":     ("bateria_min", "4000", True),
    "larga duracion":   ("bateria_min", "5000", True),
    "larga duración":   ("bateria_min", "5000", True),
    "dura mucho":       ("bateria_min", "4500", True),

    # ── BATERÍA — carga ───────────────────────────────────────────────────────
    "carga rapida":             ("carga_rapida",     "true",  True),
    "carga rápida":             ("carga_rapida",     "true",  True),
    "fast charge":              ("carga_rapida",     "true",  True),
    "carga inalambrica":        ("carga_inalambrica","true",  True),
    "carga inalámbrica":        ("carga_inalambrica","true",  True),
    "carga wireless":           ("carga_inalambrica","true",  True),
    "sin carga rapida":         ("carga_rapida",     "false", True),
    "sin carga rápida":         ("carga_rapida",     "false", True),
    "sin carga inalambrica":    ("carga_inalambrica","false", True),
    "sin carga inalámbrica":    ("carga_inalambrica","false", True),

    # ── RED MÓVIL ─────────────────────────────────────────────────────────────
    "5g":       ("red", "5G",    True),
    "4g":       ("red", "4G",    True),
    "lte":      ("red", "4G",    True),
    "3g":       ("red", "3G",    True),
    "sin 5g":   ("red_excl", "5G", False),
    "sin 4g":   ("red_excl", "4G", False),

    # ── CONECTIVIDAD ──────────────────────────────────────────────────────────
    "nfc":          ("nfc",       "true",   True),
    "sin nfc":      ("nfc",       "false",  True),
    "bluetooth":    ("bluetooth", "true",   True),
    "wifi 6":       ("wifi",      "WiFi 6", True),
    "wifi 7":       ("wifi",      "WiFi 7", True),
    "wifi6":        ("wifi",      "WiFi 6", True),
    "wifi7":        ("wifi",      "WiFi 7", True),

    # ── SIM ───────────────────────────────────────────────────────────────────
    "dual sim":     ("sim", "DualSIM", True),
    "esim":         ("sim", "eSIM",    True),
    "e-sim":        ("sim", "eSIM",    True),
    "sin esim":     ("sim_excl", "eSIM", True),

    # ── CÁMARA TRASERA ────────────────────────────────────────────────────────
    "buena camara":     ("camara_min", "50",  True),
    "buena cámara":     ("camara_min", "50",  True),
    "200mp":            ("camara_min", "200", True),
    "200 mp":           ("camara_min", "200", True),
    "108mp":            ("camara_min", "108", True),
    "108 mp":           ("camara_min", "108", True),
    "64mp":             ("camara_min", "64",  True),
    "64 mp":            ("camara_min", "64",  True),
    "50mp":             ("camara_min", "50",  True),
    "50 mp":            ("camara_min", "50",  True),
    "48mp":             ("camara_min", "48",  True),
    "48 mp":            ("camara_min", "48",  True),
    "12mp":             ("camara_min", "12",  True),
    "12 mp":            ("camara_min", "12",  True),
    "camara de 12":     ("camara_min", "12",  True),
    "camara 12":        ("camara_min", "12",  True),
    "cámara de 12":     ("camara_min", "12",  True),
    "cámara 12":        ("camara_min", "12",  True),
    "camara de 50":     ("camara_min", "50",  True),
    "camara 50":        ("camara_min", "50",  True),
    "camara de 64":     ("camara_min", "64",  True),
    "camara 64":        ("camara_min", "64",  True),
    "camara de 108":    ("camara_min", "108", True),
    "camara de 200":    ("camara_min", "200", True),
    "camara de 48":     ("camara_min", "48",  True),
    "camara 48":        ("camara_min", "48",  True),
    "cámara de 50":     ("camara_min", "50",  True),
    "cámara 50":        ("camara_min", "50",  True),
    "cámara de 64":     ("camara_min", "64",  True),
    "cámara 64":        ("camara_min", "64",  True),
    "cámara de 108":    ("camara_min", "108", True),
    "cámara de 200":    ("camara_min", "200", True),
    "resolucion 50":    ("camara_min", "50",  True),
    "resolucion 64":    ("camara_min", "64",  True),
    "alta resolucion":  ("camara_min", "64",  True),
    "alta resolución":  ("camara_min", "64",  True),

    # ── CÁMARA FRONTAL ────────────────────────────────────────────────────────
    "selfie":           ("camara_frontal_min", "16", True),
    "buena selfie":     ("camara_frontal_min", "32", True),

    # ── SENSORES ──────────────────────────────────────────────────────────────
    "huella":                   ("sensor", "SensorHuella",      True),
    "huella dactilar":          ("sensor", "SensorHuella",      True),
    "lector de huella":         ("sensor", "SensorHuella",      True),
    "sin huella":               ("sensor_excl","SensorHuella",  True),
    "reconocimiento facial":    ("sensor", "SensorFacial",      True),
    "face id":                  ("sensor", "SensorFacial",      True),
    "reconocimiento de cara":   ("sensor", "SensorFacial",      True),
    "giroscopio":               ("sensor", "SensorGiroscopio",  True),
    "sensor de luz":            ("sensor", "SensorLuz",         True),
    "luz ambiental":            ("sensor", "SensorLuz",         True),
    "sensor de proximidad":     ("sensor", "SensorProximidad",  True),

    # ── RESISTENCIA ───────────────────────────────────────────────────────────
    "resistencia al agua":      ("resistencia", "ip6",  True),
    "resistente al agua":       ("resistencia", "ip6",  True),
    "resiste agua":             ("resistencia", "ip6",  True),
    "resistencia al polvo":     ("resistencia", "ip",   True),
    "resistente al polvo":      ("resistencia", "ip",   True),
    "a prueba de agua":         ("resistencia", "ip6",  True),
    "impermeable":              ("resistencia", "ip6",  True),
    "ip68":             ("resistencia_exacta", "IP68", True),
    "ip67":             ("resistencia_exacta", "IP67", True),
    "ip64":             ("resistencia_exacta", "IP64", True),
    "ip54":             ("resistencia_exacta", "IP54", True),
    "ip53":             ("resistencia_exacta", "IP53", True),
    "sin resistencia al agua":  ("resistencia", "ip6", False),
    "sin resistencia":          ("resistencia", "ip",  False),
    "sin certificacion ip":     ("resistencia", "ip",  False),
    "sin certificación ip":     ("resistencia", "ip",  False),
    "sin ip":                   ("resistencia", "ip",  False),
    "no resistente":            ("resistencia", "ip",  False),
    "no impermeable":           ("resistencia", "ip6", False),

    # ── AUDIO ─────────────────────────────────────────────────────────────────
    "estereo":      ("audio", "Estéreo", True),
    "estéreo":      ("audio", "Estéreo", True),
    "stereo":       ("audio", "Estéreo", True),
    "audio estereo":("audio", "Estéreo", True),
    "audio estéreo":("audio", "Estéreo", True),
    "mono":         ("audio", "Mono",    True),
    "audio mono":   ("audio", "Mono",    True),
    "sin estereo":  ("audio", "Estéreo", False),
    "sin estéreo":  ("audio", "Estéreo", False),

    # ── AÑO ───────────────────────────────────────────────────────────────────
    "reciente":     ("anio_min", "2023", True),
    "nuevo":        ("anio_min", "2023", True),
    "moderno":      ("anio_min", "2023", True),
    "2024":         ("anio_min", "2024", True),
    "2023":         ("anio_min", "2023", True),
    "2022":         ("anio_min", "2022", True),
    "antiguo":      ("anio_max", "2022", True),
    "viejo":        ("anio_max", "2022", True),
}

# ── Tokens a ignorar ──────────────────────────────────────────────────────────
PALABRAS_RUIDO: set[str] = {
    "celular","celulares","telefono","teléfono","telefonos","teléfonos",
    "smartphone","smartphones","movil","móvil","moviles","móviles",
    "quiero","busco","dame","muestrame","muéstrame","mostrarme","necesito",
    "con","de","el","la","los","las","un","una","que","y","o","e",
    "tiene","tengan","tengo","para","por","en","al","del","es","ser",
    "tener","sea","sean","tenga","tengan","dispositivo","dispositivos",
    "modelo","modelos","equipo","equipos","aparato",
}

# ═══════════════════════════════════════════════════════════════════════════════
# VOCABULARIO SEMÁNTICO — INGLÉS
# Opción C de Modelización: lexicón externo multilingüe enlazado a la ontología
# ═══════════════════════════════════════════════════════════════════════════════
VOCAB_SEMANTICO_EN: dict[str, tuple[str, str, bool]] = {

    # ── TIER / RANGE ──────────────────────────────────────────────────────────
    "high end":         ("gama", "Alta",  True),
    "flagship":         ("gama", "Alta",  True),
    "premium":          ("gama", "Alta",  True),
    "top tier":         ("gama", "Alta",  True),
    "mid range":        ("gama", "Media", True),
    "mid-range":        ("gama", "Media", True),
    "midrange":         ("gama", "Media", True),
    "budget":           ("gama", "Baja",  True),
    "cheap":            ("gama", "Baja",  True),
    "affordable":       ("gama", "Baja",  True),
    "low cost":         ("gama", "Baja",  True),
    "entry level":      ("gama", "Baja",  True),
    "entry-level":      ("gama", "Baja",  True),
    "expensive":        ("gama", "Alta",  True),

    # ── OPERATING SYSTEM ──────────────────────────────────────────────────────
    "android":          ("so", "Android",   True),
    "ios":              ("so", "iOS",       True),
    "apple":            ("marca", "Apple",  True),
    "iphone":           ("marca", "Apple",  True),
    "harmonyos":        ("so", "HarmonyOS", True),
    "harmony os":       ("so", "HarmonyOS", True),

    # ── BRAND ─────────────────────────────────────────────────────────────────
    "samsung":          ("marca", "Samsung",  True),
    "xiaomi":           ("marca", "Xiaomi",   True),
    "redmi":            ("marca", "Xiaomi",   True),
    "motorola":         ("marca", "Motorola", True),
    "moto":             ("marca", "Motorola", True),
    "huawei":           ("marca", "Huawei",   True),
    "oneplus":          ("marca", "OnePlus",  True),
    "one plus":         ("marca", "OnePlus",  True),
    "oppo":             ("marca", "Oppo",     True),
    "realme":           ("marca", "Realme",   True),
    "vivo":             ("marca", "Vivo",     True),

    # ── PROCESSOR ─────────────────────────────────────────────────────────────
    "qualcomm":         ("cpu", "Qualcomm", True),
    "snapdragon":       ("cpu", "Qualcomm", True),
    "mediatek":         ("cpu", "MediaTek", True),
    "dimensity":        ("cpu", "MediaTek", True),
    "helio":            ("cpu", "MediaTek", True),
    "exynos":           ("cpu", "Samsung",  True),
    "kirin":            ("cpu", "Huawei",   True),
    "bionic":           ("cpu", "Apple",    True),
    "octa core":        ("nucleos", "8", True),
    "8 cores":          ("nucleos", "8", True),

    # ── RAM ───────────────────────────────────────────────────────────────────
    "4gb ram":          ("ram", "4",  True),
    "4 gb ram":         ("ram", "4",  True),
    "6gb ram":          ("ram", "6",  True),
    "6 gb ram":         ("ram", "6",  True),
    "8gb ram":          ("ram", "8",  True),
    "8 gb ram":         ("ram", "8",  True),
    "12gb ram":         ("ram", "12", True),
    "12 gb ram":        ("ram", "12", True),
    "16gb ram":         ("ram", "16", True),
    "16 gb ram":        ("ram", "16", True),
    "lots of ram":      ("ram_min", "12", True),
    "plenty of ram":    ("ram_min", "8",  True),
    "little ram":       ("ram_max", "6",  True),

    # ── STORAGE ───────────────────────────────────────────────────────────────
    "64gb":             ("almacenamiento", "64",   True),
    "128gb":            ("almacenamiento", "128",  True),
    "256gb":            ("almacenamiento", "256",  True),
    "512gb":            ("almacenamiento", "512",  True),
    "1tb":              ("almacenamiento", "1024", True),
    "64 gb":            ("almacenamiento", "64",   True),
    "128 gb":           ("almacenamiento", "128",  True),
    "256 gb":           ("almacenamiento", "256",  True),
    "512 gb":           ("almacenamiento", "512",  True),
    "lot of storage":   ("almacenamiento", "256",  True),
    "lots of storage":  ("almacenamiento", "256",  True),

    # ── MICROSD ───────────────────────────────────────────────────────────────
    "microsd":          ("microsd", "true",  True),
    "sd card":          ("microsd", "true",  True),
    "expandable":       ("microsd", "true",  True),
    "no sd card":       ("microsd", "false", True),
    "no microsd":       ("microsd", "false", True),

    # ── DISPLAY ───────────────────────────────────────────────────────────────
    "amoled":           ("pantalla", "AMOLED",         True),
    "dynamic amoled":   ("pantalla", "Dynamic AMOLED", True),
    "oled":             ("pantalla", "OLED",           True),
    "lcd":              ("pantalla", "LCD",            True),
    "big screen":       ("pantalla_min", "68", True),
    "large screen":     ("pantalla_min", "68", True),
    "small screen":     ("pantalla_max", "62", True),
    "compact":          ("pantalla_max", "62", True),
    "120hz":            ("refresco", "120", True),
    "120 hz":           ("refresco", "120", True),
    "90hz":             ("refresco", "90",  True),
    "90 hz":            ("refresco", "90",  True),
    "60hz":             ("refresco", "60",  True),
    "high refresh":     ("refresco_min", "90", True),
    "smooth display":   ("refresco_min", "90", True),

    # ── BATTERY ───────────────────────────────────────────────────────────────
    "big battery":      ("bateria_min", "5000", True),
    "large battery":    ("bateria_min", "5000", True),
    "good battery":     ("bateria_min", "4500", True),
    "long battery":     ("bateria_min", "5000", True),
    "long lasting":     ("bateria_min", "4500", True),
    "5000mah":          ("bateria_min", "5000", True),
    "5000 mah":         ("bateria_min", "5000", True),
    "4000mah":          ("bateria_min", "4000", True),
    "4000 mah":         ("bateria_min", "4000", True),
    "fast charge":      ("carga_rapida",     "true", True),
    "fast charging":    ("carga_rapida",     "true", True),
    "wireless charge":  ("carga_inalambrica","true", True),
    "wireless charging":("carga_inalambrica","true", True),
    "no fast charge":   ("carga_rapida",     "false", True),
    "no wireless":      ("carga_inalambrica","false", True),

    # ── NETWORK ───────────────────────────────────────────────────────────────
    "5g":       ("red", "5G", True),
    "4g":       ("red", "4G", True),
    "lte":      ("red", "4G", True),
    "3g":       ("red", "3G", True),
    "no 5g":    ("red_excl", "5G", False),

    # ── CONNECTIVITY ──────────────────────────────────────────────────────────
    "nfc":          ("nfc",       "true",   True),
    "no nfc":       ("nfc",       "false",  True),
    "bluetooth":    ("bluetooth", "true",   True),
    "wifi 6":       ("wifi",      "WiFi 6", True),
    "wifi 7":       ("wifi",      "WiFi 7", True),
    "dual sim":     ("sim", "DualSIM", True),
    "esim":         ("sim", "eSIM",    True),
    "e-sim":        ("sim", "eSIM",    True),

    # ── CAMERA ────────────────────────────────────────────────────────────────
    "good camera":      ("camara_min", "50",  True),
    "great camera":     ("camara_min", "64",  True),
    "200mp":            ("camara_min", "200", True),
    "200 mp":           ("camara_min", "200", True),
    "64mp":             ("camara_min", "64",  True),
    "64 mp":            ("camara_min", "64",  True),
    "50mp":             ("camara_min", "50",  True),
    "50 mp":            ("camara_min", "50",  True),
    "48mp":             ("camara_min", "48",  True),
    "48 mp":            ("camara_min", "48",  True),
    "selfie":           ("camara_frontal_min", "16", True),
    "good selfie":      ("camara_frontal_min", "32", True),
    "high resolution":  ("camara_min", "64",  True),

    # ── SENSORS ───────────────────────────────────────────────────────────────
    "fingerprint":      ("sensor", "SensorHuella",     True),
    "face recognition": ("sensor", "SensorFacial",     True),
    "face id":          ("sensor", "SensorFacial",     True),
    "gyroscope":        ("sensor", "SensorGiroscopio", True),
    "light sensor":     ("sensor", "SensorLuz",        True),
    "proximity sensor": ("sensor", "SensorProximidad", True),

    # ── WATER RESISTANCE ──────────────────────────────────────────────────────
    "waterproof":       ("resistencia", "ip6",  True),
    "water resistant":  ("resistencia", "ip6",  True),
    "water resistance": ("resistencia", "ip6",  True),
    "dust proof":       ("resistencia", "ip",   True),
    "ip68":             ("resistencia_exacta", "IP68", True),
    "ip67":             ("resistencia_exacta", "IP67", True),
    "ip54":             ("resistencia_exacta", "IP54", True),
    "not waterproof":   ("resistencia", "ip6",  False),
    "no ip":            ("resistencia", "ip",   False),

    # ── AUDIO ─────────────────────────────────────────────────────────────────
    "stereo":           ("audio", "Estéreo", True),
    "stereo speakers":  ("audio", "Estéreo", True),
    "mono":             ("audio", "Mono",    True),
    "no stereo":        ("audio", "Estéreo", False),

    # ── YEAR ──────────────────────────────────────────────────────────────────
    "recent":           ("anio_min", "2023", True),
    "new":              ("anio_min", "2023", True),
    "latest":           ("anio_min", "2024", True),
    "modern":           ("anio_min", "2023", True),
    "2024":             ("anio_min", "2024", True),
    "2023":             ("anio_min", "2023", True),
    "2022":             ("anio_min", "2022", True),
    "old":              ("anio_max", "2022", True),
    "older":            ("anio_max", "2022", True),
}

PALABRAS_RUIDO_EN: set[str] = {
    "phone", "phones", "smartphone", "smartphones", "mobile", "device", "devices",
    "cell", "cellphone", "cellphones", "handset", "handsets", "model", "models",
    "i", "want", "show", "me", "need", "find", "looking", "for", "with",
    "the", "a", "an", "that", "has", "have", "and", "or", "of", "in", "to",
    "get", "give", "list", "any", "some", "which",
}

PREFIJOS_NEGACION_EN: list[str] = [
    "without ", "no ", "not ", "doesn't have ", "don't have ",
    "without having ", "lacking ",
]

# ═══════════════════════════════════════════════════════════════════════════════
# VOCABULARIO SEMÁNTICO — PORTUGUÉS
# Opción C de Modelização: léxico externo multilíngue ligado à ontologia
# ═══════════════════════════════════════════════════════════════════════════════
VOCAB_SEMANTICO_PT: dict[str, tuple[str, str, bool]] = {

    # ── FAIXA / GAMA ──────────────────────────────────────────────────────────
    "top de linha":     ("gama", "Alta",  True),
    "alto desempenho":  ("gama", "Alta",  True),
    "premium":          ("gama", "Alta",  True),
    "flagship":         ("gama", "Alta",  True),
    "intermediario":    ("gama", "Media", True),
    "intermediário":    ("gama", "Media", True),
    "linha media":      ("gama", "Media", True),
    "linha média":      ("gama", "Media", True),
    "basico":           ("gama", "Baja",  True),
    "básico":           ("gama", "Baja",  True),
    "barato":           ("gama", "Baja",  True),
    "baratos":          ("gama", "Baja",  True),
    "acessivel":        ("gama", "Baja",  True),
    "acessível":        ("gama", "Baja",  True),
    "entrada":          ("gama", "Baja",  True),
    "caro":             ("gama", "Alta",  True),

    # ── SISTEMA OPERACIONAL ───────────────────────────────────────────────────
    "android":          ("so", "Android",   True),
    "ios":              ("so", "iOS",       True),
    "apple":            ("marca", "Apple",  True),
    "iphone":           ("marca", "Apple",  True),
    "harmonyos":        ("so", "HarmonyOS", True),

    # ── MARCA ─────────────────────────────────────────────────────────────────
    "samsung":          ("marca", "Samsung",  True),
    "xiaomi":           ("marca", "Xiaomi",   True),
    "redmi":            ("marca", "Xiaomi",   True),
    "motorola":         ("marca", "Motorola", True),
    "moto":             ("marca", "Motorola", True),
    "huawei":           ("marca", "Huawei",   True),
    "oneplus":          ("marca", "OnePlus",  True),
    "oppo":             ("marca", "Oppo",     True),
    "realme":           ("marca", "Realme",   True),
    "vivo":             ("marca", "Vivo",     True),

    # ── PROCESSADOR ───────────────────────────────────────────────────────────
    "qualcomm":         ("cpu", "Qualcomm", True),
    "snapdragon":       ("cpu", "Qualcomm", True),
    "mediatek":         ("cpu", "MediaTek", True),
    "dimensity":        ("cpu", "MediaTek", True),
    "helio":            ("cpu", "MediaTek", True),
    "exynos":           ("cpu", "Samsung",  True),
    "kirin":            ("cpu", "Huawei",   True),
    "bionic":           ("cpu", "Apple",    True),
    "octa core":        ("nucleos", "8", True),
    "oito nucleos":     ("nucleos", "8", True),
    "oito núcleos":     ("nucleos", "8", True),

    # ── RAM ───────────────────────────────────────────────────────────────────
    "4gb ram":          ("ram", "4",  True),
    "4 gb ram":         ("ram", "4",  True),
    "6gb ram":          ("ram", "6",  True),
    "6 gb ram":         ("ram", "6",  True),
    "8gb ram":          ("ram", "8",  True),
    "8 gb ram":         ("ram", "8",  True),
    "12gb ram":         ("ram", "12", True),
    "12 gb ram":        ("ram", "12", True),
    "16gb ram":         ("ram", "16", True),
    "16 gb ram":        ("ram", "16", True),
    "muita ram":        ("ram_min", "12", True),
    "bastante ram":     ("ram_min", "8",  True),
    "pouca ram":        ("ram_max", "6",  True),

    # ── ARMAZENAMENTO ─────────────────────────────────────────────────────────
    "64gb":             ("almacenamiento", "64",   True),
    "128gb":            ("almacenamiento", "128",  True),
    "256gb":            ("almacenamiento", "256",  True),
    "512gb":            ("almacenamiento", "512",  True),
    "1tb":              ("almacenamiento", "1024", True),
    "64 gb":            ("almacenamiento", "64",   True),
    "128 gb":           ("almacenamiento", "128",  True),
    "256 gb":           ("almacenamiento", "256",  True),
    "512 gb":           ("almacenamiento", "512",  True),
    "muito armazenamento": ("almacenamiento", "256", True),
    "pouco armazenamento": ("almacenamiento", "64",  True),

    # ── MICROSD ───────────────────────────────────────────────────────────────
    "microsd":          ("microsd", "true",  True),
    "cartao sd":        ("microsd", "true",  True),
    "cartão sd":        ("microsd", "true",  True),
    "memoria expansivel":("microsd", "true", True),
    "memória expansível":("microsd", "true", True),
    "sem microsd":      ("microsd", "false", True),
    "sem cartao sd":    ("microsd", "false", True),

    # ── TELA ──────────────────────────────────────────────────────────────────
    "amoled":           ("pantalla", "AMOLED",         True),
    "dynamic amoled":   ("pantalla", "Dynamic AMOLED", True),
    "oled":             ("pantalla", "OLED",           True),
    "lcd":              ("pantalla", "LCD",            True),
    "tela grande":      ("pantalla_min", "68", True),
    "tela pequena":     ("pantalla_max", "62", True),
    "compacto":         ("pantalla_max", "62", True),
    "120hz":            ("refresco", "120", True),
    "120 hz":           ("refresco", "120", True),
    "90hz":             ("refresco", "90",  True),
    "90 hz":            ("refresco", "90",  True),
    "alta taxa":        ("refresco_min", "90", True),

    # ── BATERIA ───────────────────────────────────────────────────────────────
    "bateria grande":   ("bateria_min", "5000", True),
    "boa bateria":      ("bateria_min", "4500", True),
    "muita bateria":    ("bateria_min", "5000", True),
    "bateria duravel":  ("bateria_min", "4500", True),
    "bateria durável":  ("bateria_min", "4500", True),
    "5000mah":          ("bateria_min", "5000", True),
    "5000 mah":         ("bateria_min", "5000", True),
    "4000mah":          ("bateria_min", "4000", True),
    "4000 mah":         ("bateria_min", "4000", True),
    "carga rapida":     ("carga_rapida",     "true", True),
    "carga rápida":     ("carga_rapida",     "true", True),
    "carregamento rapido":  ("carga_rapida", "true", True),
    "carregamento rápido":  ("carga_rapida", "true", True),
    "carga sem fio":    ("carga_inalambrica","true", True),
    "carga wireless":   ("carga_inalambrica","true", True),
    "sem carga rapida": ("carga_rapida",     "false", True),
    "sem carga rápida": ("carga_rapida",     "false", True),

    # ── REDE MÓVEL ────────────────────────────────────────────────────────────
    "5g":       ("red", "5G", True),
    "4g":       ("red", "4G", True),
    "lte":      ("red", "4G", True),
    "3g":       ("red", "3G", True),
    "sem 5g":   ("red_excl", "5G", False),

    # ── CONECTIVIDADE ─────────────────────────────────────────────────────────
    "nfc":          ("nfc",       "true",   True),
    "sem nfc":      ("nfc",       "false",  True),
    "bluetooth":    ("bluetooth", "true",   True),
    "wifi 6":       ("wifi",      "WiFi 6", True),
    "wifi 7":       ("wifi",      "WiFi 7", True),
    "dual sim":     ("sim", "DualSIM", True),
    "esim":         ("sim", "eSIM",    True),

    # ── CAMERA ────────────────────────────────────────────────────────────────
    "boa camera":       ("camara_min", "50",  True),
    "boa câmera":       ("camara_min", "50",  True),
    "otima camera":     ("camara_min", "64",  True),
    "ótima câmera":     ("camara_min", "64",  True),
    "200mp":            ("camara_min", "200", True),
    "200 mp":           ("camara_min", "200", True),
    "64mp":             ("camara_min", "64",  True),
    "64 mp":            ("camara_min", "64",  True),
    "50mp":             ("camara_min", "50",  True),
    "50 mp":            ("camara_min", "50",  True),
    "48mp":             ("camara_min", "48",  True),
    "48 mp":            ("camara_min", "48",  True),
    "selfie":           ("camara_frontal_min", "16", True),
    "boa selfie":       ("camara_frontal_min", "32", True),
    "alta resolucao":   ("camara_min", "64",  True),
    "alta resolução":   ("camara_min", "64",  True),

    # ── SENSORES ──────────────────────────────────────────────────────────────
    "impressao digital":    ("sensor", "SensorHuella",     True),
    "impressão digital":    ("sensor", "SensorHuella",     True),
    "leitor de digital":    ("sensor", "SensorHuella",     True),
    "reconhecimento facial":("sensor", "SensorFacial",     True),
    "giroscopio":           ("sensor", "SensorGiroscopio", True),
    "giroscópio":           ("sensor", "SensorGiroscopio", True),
    "sensor de luz":        ("sensor", "SensorLuz",        True),
    "sensor de proximidade":("sensor", "SensorProximidad", True),

    # ── RESISTÊNCIA ───────────────────────────────────────────────────────────
    "a prova dagua":    ("resistencia", "ip6",  True),
    "à prova d'água":   ("resistencia", "ip6",  True),
    "resistente agua":  ("resistencia", "ip6",  True),
    "resistente à água":("resistencia", "ip6",  True),
    "ip68":             ("resistencia_exacta", "IP68", True),
    "ip67":             ("resistencia_exacta", "IP67", True),
    "sem resistencia":  ("resistencia", "ip",   False),
    "sem ip":           ("resistencia", "ip",   False),

    # ── AUDIO ─────────────────────────────────────────────────────────────────
    "estereo":          ("audio", "Estéreo", True),
    "estéreo":          ("audio", "Estéreo", True),
    "stereo":           ("audio", "Estéreo", True),
    "mono":             ("audio", "Mono",    True),
    "sem estereo":      ("audio", "Estéreo", False),

    # ── ANO ───────────────────────────────────────────────────────────────────
    "recente":          ("anio_min", "2023", True),
    "novo":             ("anio_min", "2023", True),
    "moderno":          ("anio_min", "2023", True),
    "lancamento":       ("anio_min", "2024", True),
    "lançamento":       ("anio_min", "2024", True),
    "2024":             ("anio_min", "2024", True),
    "2023":             ("anio_min", "2023", True),
    "2022":             ("anio_min", "2022", True),
    "antigo":           ("anio_max", "2022", True),
    "velho":            ("anio_max", "2022", True),
}

PALABRAS_RUIDO_PT: set[str] = {
    "celular", "celulares", "telefone", "telefones", "smartphone", "smartphones",
    "movel", "móvel", "moveis", "móveis", "dispositivo", "dispositivos",
    "modelo", "modelos", "aparelho", "aparelhos",
    "quero", "procuro", "mostre", "preciso", "busco",
    "com", "de", "o", "a", "os", "as", "um", "uma", "que", "e", "ou",
    "tem", "tenha", "tenham", "para", "por", "em", "ao", "do", "da",
    "ter", "seja", "sejam",
}

PREFIJOS_NEGACION_PT: list[str] = [
    "sem ", "não tem ", "não tenha ", "sem ter ",
    "que não tenha ", "que não tenham ", "não ",
]

# ── Prefijos de negación ──────────────────────────────────────────────────────
PREFIJOS_NEGACION: list[str] = [
    "sin ", "no tiene ", "no tengan ", "sin tener ",
    "que no tenga ", "que no tengan ", "no ",
]


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE APOYO
# ═══════════════════════════════════════════════════════════════════════════════

def _normalizar(texto: str) -> str:
    """Lowercase, colapsa espacios, elimina puntuación (excepto guiones)."""
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\s\-]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def _fuzzy_match_ngrams(texto: str, umbral: float = 0.78, vocab: dict = None) -> list[tuple]:
    """
    Divide el texto en n-gramas de 1–4 palabras y los compara contra el vocabulario activo.
    Si no se pasa vocab, usa VOCAB_SEMANTICO (español por defecto).
    """
    if vocab is None:
        vocab = VOCAB_SEMANTICO
    palabras = texto.split()
    encontrados: list[tuple] = []
    usados: set[int] = set()

    for n in range(4, 0, -1):
        for i in range(len(palabras) - n + 1):
            if any(j in usados for j in range(i, i + n)):
                continue
            ngram = " ".join(palabras[i:i + n])
            mejor_score, mejor = 0.0, None
            for clave, (cat, val, pos) in vocab.items():
                score = SequenceMatcher(None, ngram, clave).ratio()
                if score > mejor_score:
                    mejor_score = score
                    mejor = (cat, val, pos, clave)
            if mejor_score >= umbral and mejor:
                encontrados.append(mejor + (mejor_score,))
                for j in range(i, i + n):
                    usados.add(j)

    return encontrados


def _snap_valor(cat: str, val: str) -> str:
    """
    Para categorías numéricas, ajusta val al valor real más cercano (>= val).
    Si no hay snap disponible (val ya es exacto o no aplica), retorna val tal cual.
    """
    try:
        n = int(val)
    except (ValueError, TypeError):
        return val

    if cat == "camara_min":
        snapped = _snap_superior(n, _CAMARA_TRASERA_UNICOS)
        return str(snapped) if snapped else val
    if cat == "camara_frontal_min":
        snapped = _snap_superior(n, _CAMARA_FRONTAL_UNICOS)
        return str(snapped) if snapped else val
    if cat == "ram":
        snapped = _snap_superior(n, _RAM_UNICOS)
        return str(snapped) if snapped else val
    if cat == "ram_min":
        snapped = _snap_superior(n, _RAM_UNICOS)
        return str(snapped) if snapped else val
    if cat == "almacenamiento":
        snapped = _snap_superior(n, _STORAGE_UNICOS)
        return str(snapped) if snapped else val
    if cat == "bateria_min":
        snapped = _snap_superior(n, _BATERIA_UNICOS)
        return str(snapped) if snapped else val
    if cat == "bateria_max":
        snapped = _snap_inferior(n, _BATERIA_UNICOS)
        return str(snapped) if snapped else val
    if cat == "refresco":
        snapped = _snap_superior(n, _REFRESCO_UNICOS)
        return str(snapped) if snapped else val
    if cat == "refresco_min":
        snapped = _snap_superior(n, _REFRESCO_UNICOS)
        return str(snapped) if snapped else val
    return val


def _aplicar_filtro(filtros: dict, cat: str, val: str, negado: bool) -> bool:
    """Escribe el valor detectado en el dict de filtros (con snap numérico)."""
    # Snap para categorías numéricas que vienen del vocab o fuzzy
    val = _snap_valor(cat, val)
    if cat == "resistencia":
        if negado:
            if not filtros["resistencia_neg"]:
                filtros["resistencia_neg"] = val
                filtros["negaciones"].append(f"sin certificación {val.upper()}")
                return True
        else:
            if not filtros["resistencia"]:
                filtros["resistencia"] = val
                return True
    elif cat == "audio":
        if negado:
            if not filtros["audio_neg"]:
                filtros["audio_neg"] = val
                filtros["negaciones"].append(f"sin audio {val}")
                return True
        else:
            if not filtros["audio"]:
                filtros["audio"] = val
                return True
    elif cat == "sensor":
        if negado:
            if not filtros["sensor_excl"]:
                filtros["sensor_excl"] = val
                filtros["negaciones"].append(f"sin {val}")
                return True
        else:
            if not filtros.get("sensor"):
                filtros["sensor"] = val
                return True
    elif cat == "nfc":
        if not filtros["nfc"]:
            filtros["nfc"] = val
            if val == "false":
                filtros["negaciones"].append("sin NFC")
            return True
    elif cat in filtros and not filtros[cat]:
        filtros[cat] = val
        return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACCIÓN NUMÉRICA MEJORADA  —  con lógica de proximidad para precio
# ═══════════════════════════════════════════════════════════════════════════════

def _extraer_numericos(texto: str, filtros: dict, lang: str = "es") -> str:
    """
    Extrae valores numéricos explícitos y los convierte en filtros.
    Soporta idiomas: "es" (español), "en" (inglés), "pt" (portugués).

    LÓGICA DE PRECIO (nueva):
    ─────────────────────────
    • "precio 300", "300 dólares", "$300" sin operador:
        Si 300 existe en _PRECIOS_UNICOS → precio_exacto = 300 (precio_min = precio_max = 300).
        Si NO existe → snap_al_precio_real(300) = 450 → precio_min = 450, precio_modo = "rango".
        Resultado: muestra desde 450 en adelante ordenado ASC.

    • "hasta 500", "menos de 500", "precio máximo 500":
        precio_max = 500, precio_modo = "maximo".

    • "más de 300", "desde 300", "mínimo 300", "300 para arriba":
        precio_min = snap_superior(300) = 450, precio_modo = "minimo".

    Retorna el texto con fragmentos consumidos reemplazados por espacios.
    """
    t = texto

    # ════════════════════════════════════════════════════════════════════════════
    # PATRONES POR IDIOMA
    # ════════════════════════════════════════════════════════════════════════════

    if lang == "en":
        # ── Battery — explicit operator ──────────────────────────────────────
        _pat_bateria_min = r'(?:more\s+than|greater\s+than|at\s+least|minimum|over)\s*(\d{4,5})\s*(?:mah)?'
        _pat_bateria_max = r'(?:less\s+than|under|maximum|max|up\s+to|no\s+more\s+than)\s*(\d{4,5})\s*(?:mah)?'
        _pat_bateria_kw  = r'battery\s+(?:of\s+)?(\d{4,5})'

        # ── Price — minimum operator ─────────────────────────────────────────
        _pat_precio_min = (
            r'(?:price\s+)?(?:more\s+than|greater\s+than|at\s+least|minimum|min|over|from|starting\s+(?:at|from))'
            r'\s*\$?\s*(\d{2,5})\s*(?:dollars?|usd)?'
        )
        _pat_precio_min2 = (
            r'\b(\d{2,5})\s*(?:dollars?|usd)?\s+(?:and\s+(?:above|up)|or\s+(?:more|above)|and\s+over)'
        )
        # ── Price — maximum operator ─────────────────────────────────────────
        _pat_precio_max = (
            r'(?:price\s+)?(?:less\s+than|under|maximum|max|up\s+to|no\s+more\s+than|below|cheaper\s+than)'
            r'\s*\$?\s*(\d{2,5})\s*(?:dollars?|usd)?'
        )
        # ── Price — no operator ───────────────────────────────────────────────
        _pat_precio_bare = (
            r'\bprice\s+\$?\s*(\d{2,5})\b'                          # "price 300"
            r'|\$\s*(\d{2,5})\b'                                      # "$300"
            r'|\b(\d{2,5})\s*(?:dollars?|usd)\b'                     # "300 dollars"
            r'|(?:costs?\s+|worth\s+)\$?\s*(\d{2,5})\b'             # "costs 300"
        )
        # ── Camera — front / rear keywords ───────────────────────────────────
        _pat_camara_frontal = r'(?:front\s+camera|front\s+cam|selfie\s+camera)\s+(?:of\s+)?(\d{1,3})\s*(?:mp)?'
        _pat_camara_kw      = r'(?:camera\s+(?:of\s+)?|resolution\s+(?:of\s+)?)?(\d{2,3})\s*(?:mp|megapixels?)'
        _pat_camara_kw2     = r'(?:camera|cam)\s+(?:of\s+)?(\d{2,3})\b'
        # ── Battery capacity keyword ──────────────────────────────────────────
        _pat_capacidad      = r'(?:capacity|battery\s+capacity)\s+(?:of\s+)?(\d{4,5})'
        # ── Storage keyword ───────────────────────────────────────────────────
        _pat_storage_kw     = r'(?:storage|internal\s+storage|internal\s+memory|space)\s+(?:of\s+)?(\d{2,4})\b'

    elif lang == "pt":
        # ── Battery — explicit operator ──────────────────────────────────────
        _pat_bateria_min = r'(?:mais\s+de|maior(?:es)?\s+(?:que|de)|m[ií]nimo|pelo\s+menos)\s*(\d{4,5})\s*(?:mah)?'
        _pat_bateria_max = r'(?:menos\s+de|menor(?:es)?\s+(?:que|de)|m[aá]ximo|at[eé]|no\s+m[aá]ximo\s+de)\s*(\d{4,5})\s*(?:mah)?'
        _pat_bateria_kw  = r'bater(?:ia|ia)\s+(?:de\s+)?(\d{4,5})'

        # ── Price — minimum operator ─────────────────────────────────────────
        _pat_precio_min = (
            r'(?:pre[cç]o\s+)?(?:mais\s+de|maior(?:es)?\s+(?:que|de)|m[ií]nimo|pelo\s+menos|a\s+partir\s+de|desde)'
            r'\s*\$?\s*(\d{2,5})\s*(?:reais?|brl|d[oó]lares?|usd)?'
        )
        _pat_precio_min2 = (
            r'\b(\d{2,5})\s*(?:reais?|brl|d[oó]lares?|usd)?\s+(?:ou\s+mais|para\s+cima|em\s+diante)'
        )
        # ── Price — maximum operator ─────────────────────────────────────────
        _pat_precio_max = (
            r'(?:pre[cç]o\s+)?(?:menos\s+de|menor(?:es)?\s+(?:que|de)|m[aá]ximo|at[eé]|no\s+m[aá]ximo\s+de|por\s+menos\s+de)'
            r'\s*\$?\s*(\d{2,5})\s*(?:reais?|brl|d[oó]lares?|usd)?'
        )
        # ── Price — no operator ───────────────────────────────────────────────
        _pat_precio_bare = (
            r'\bpre[cç]o\s+\$?\s*(\d{2,5})\b'                        # "preço 300"
            r'|\$\s*(\d{2,5})\b'                                       # "$300"
            r'|\b(\d{2,5})\s*(?:reais?|brl|d[oó]lares?|usd)\b'      # "300 reais"
            r'|(?:custa[m]?\s+|vale[m]?\s+)\$?\s*(\d{2,5})\b'        # "custa 300"
        )
        # ── Camera — front / rear keywords ───────────────────────────────────
        _pat_camara_frontal = r'(?:c[aâ]mera\s+frontal|frontal|selfie)\s+(?:de\s+)?(\d{1,3})\s*(?:mp)?'
        _pat_camara_kw      = r'(?:c[aâ]mera\s+(?:de\s+)?|resolu[cç][aã]o\s+(?:de\s+)?)?(\d{2,3})\s*(?:mp|megapixels?)'
        _pat_camara_kw2     = r'c[aâ]mera\s+(?:de\s+)?(\d{2,3})\b'
        # ── Battery capacity keyword ──────────────────────────────────────────
        _pat_capacidad      = r'(?:capacidade)\s+(?:de\s+)?(\d{4,5})'
        # ── Storage keyword ───────────────────────────────────────────────────
        _pat_storage_kw     = r'(?:armazenamento|mem[oó]ria\s+interna|espa[cç]o)\s+(?:de\s+)?(\d{2,4})\b'

    else:  # "es" — patrones originales
        # ── Battery — explicit operator ──────────────────────────────────────
        _pat_bateria_min = r'(?:mayor(?:es)?\s+(?:a|de)|mas\s+de|m[aá]s\s+de|m[ií]nimo|al\s+menos)\s*(\d{4,5})\s*(?:mah)?'
        _pat_bateria_max = r'(?:menor(?:es)?\s+(?:a|de)|menos\s+de|m[aá]ximo|hasta|no\s+m[aá]s\s+de)\s*(\d{4,5})\s*(?:mah)?'
        _pat_bateria_kw  = r'bater[ií]a\s+(?:de\s+)?(\d{4,5})'

        # ── Price — minimum operator ─────────────────────────────────────────
        _pat_precio_min = (
            r'(?:precio\s+)?(?:mayor(?:es)?\s+(?:a|de)|mas\s+de|m[aá]s\s+de|m[ií]nimo|al\s+menos|desde'
            r'|de\s+(?:\$\s*)?\d+\s+para\s+arriba)'
            r'\s*\$?\s*(\d{2,5})\s*(?:d[oó]lares?|usd)?'
        )
        _pat_precio_min2 = (
            r'\b(\d{2,5})\s*(?:d[oó]lares?|usd)?\s+(?:para\s+arriba|en\s+adelante|o\s+m[aá]s)'
        )
        # ── Price — maximum operator ─────────────────────────────────────────
        _pat_precio_max = (
            r'(?:precio\s+)?(?:menor(?:es)?\s+(?:a|de)|menos\s+de|m[aá]ximo|hasta|no\s+m[aá]s\s+de|por\s+menos\s+de)'
            r'\s*\$?\s*(\d{2,5})\s*(?:d[oó]lares?|usd)?'
        )
        # ── Price — no operator ───────────────────────────────────────────────
        _pat_precio_bare = (
            r'\bprecio\s+\$?\s*(\d{2,5})\b'           # "precio 300"
            r'|\$\s*(\d{2,5})\b'                        # "$300"
            r'|\b(\d{2,5})\s*(?:d[oó]lares?|usd)\b'   # "300 dólares"
            r'|(?:cuestan?|cuesta|valen?|vale)\s+\$?\s*(\d{2,5})\b'  # "cuestan 300"
        )
        # ── Camera — front / rear keywords ───────────────────────────────────
        _pat_camara_frontal = r'(?:c[aá]mara\s+frontal|frontal|selfie)\s+(?:de\s+)?(\d{1,3})\s*(?:mp)?'
        _pat_camara_kw      = r'(?:c[aá]mara\s+(?:de\s+)?|resoluci[oó]n\s+(?:de\s+)?)?(\d{2,3})\s*(?:mp|megap[ií]xeles?|megap[ií]xel)'
        _pat_camara_kw2     = r'c[aá]mara\s+(?:de\s+)?(\d{2,3})\b'
        # ── Battery capacity keyword ──────────────────────────────────────────
        _pat_capacidad      = r'capacidad\s+(?:de\s+)?(\d{4,5})'
        # ── Storage keyword ───────────────────────────────────────────────────
        _pat_storage_kw     = r'(?:almacenamiento|memoria\s+interna|espacio)\s+(?:de\s+)?(\d{2,4})\b'

    # ════════════════════════════════════════════════════════════════════════════
    # APLICACIÓN DE PATRONES (común para los tres idiomas)
    # ════════════════════════════════════════════════════════════════════════════

    # ── Batería — operador mínimo ─────────────────────────────────────────────
    for m in re.finditer(_pat_bateria_min, t, re.IGNORECASE):
        val = m.group(1) if m.lastindex == 1 else (m.group(2) if m.lastindex >= 2 else None)
        # Para los patrones donde el número puede estar en distintos grupos:
        val = next((m.group(i) for i in range(1, (m.lastindex or 0) + 1) if m.group(i) and m.group(i).isdigit() and len(m.group(i)) >= 4), None)
        if val:
            snapped = _snap_superior(int(val), _BATERIA_UNICOS)
            if not filtros["bateria_min"] and snapped:
                filtros["bateria_min"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Batería — operador máximo ─────────────────────────────────────────────
    for m in re.finditer(_pat_bateria_max, t, re.IGNORECASE):
        val = next((m.group(i) for i in range(1, (m.lastindex or 0) + 1) if m.group(i) and m.group(i).isdigit() and len(m.group(i)) >= 4), None)
        if val:
            snapped = _snap_inferior(int(val), _BATERIA_UNICOS)
            if not filtros["bateria_max"] and snapped:
                filtros["bateria_max"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Batería — número + mah sin operador ──────────────────────────────────
    for m in re.finditer(r'\b(\d{4,5})\s*mah\b', t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros["bateria_min"]:
            snapped = _snap_superior(val, _BATERIA_UNICOS) or str(val)
            filtros["bateria_min"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Batería — palabra clave + número ─────────────────────────────────────
    for m in re.finditer(_pat_bateria_kw, t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros["bateria_min"]:
            snapped = _snap_superior(val, _BATERIA_UNICOS) or str(val)
            filtros["bateria_min"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Precio — operador mínimo ──────────────────────────────────────────────
    for m in re.finditer(_pat_precio_min, t, re.IGNORECASE):
        val = next((m.group(i) for i in range(1, (m.lastindex or 0) + 1) if m.group(i) and re.match(r'^\d{2,5}$', m.group(i))), None)
        if val:
            val = int(val)
            if not filtros.get("precio_min"):
                snapped = snap_al_precio_real(val)
                if snapped:
                    filtros["precio_min"] = str(snapped)
                    filtros["precio_modo"] = "minimo"
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Precio — "NNN para arriba / or more / ou mais" ───────────────────────
    for m in re.finditer(_pat_precio_min2, t, re.IGNORECASE):
        val = next((m.group(i) for i in range(1, (m.lastindex or 0) + 1) if m.group(i) and re.match(r'^\d{2,5}$', m.group(i))), None)
        if val:
            val = int(val)
            if not filtros.get("precio_min"):
                snapped = snap_al_precio_real(val)
                if snapped:
                    filtros["precio_min"] = str(snapped)
                    filtros["precio_modo"] = "minimo"
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Precio — operador máximo ──────────────────────────────────────────────
    for m in re.finditer(_pat_precio_max, t, re.IGNORECASE):
        val = next((m.group(i) for i in range(1, (m.lastindex or 0) + 1) if m.group(i) and re.match(r'^\d{2,5}$', m.group(i))), None)
        if val:
            val = int(val)
            if not filtros.get("precio_max"):
                filtros["precio_max"] = str(val)
                filtros["precio_modo"] = "maximo"
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Precio — sin operador ─────────────────────────────────────────────────
    for m in re.finditer(_pat_precio_bare, t, re.IGNORECASE):
        val = next((m.group(i) for i in range(1, (m.lastindex or 0) + 1) if m.group(i) and re.match(r'^\d{2,5}$', m.group(i))), None)
        if val:
            val = int(val)
            if not filtros.get("precio_min") and not filtros.get("precio_max"):
                if val in _PRECIOS_UNICOS:
                    filtros["precio_min"] = str(val)
                    filtros["precio_modo"] = "rango"
                else:
                    snapped = snap_al_precio_real(val)
                    if snapped:
                        filtros["precio_min"] = str(snapped)
                        filtros["precio_modo"] = "rango"
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Cámara frontal — PRIMERO para que no sea capturada por el regex trasero ─
    for m in re.finditer(_pat_camara_frontal, t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros.get("camara_frontal_min"):
            snapped = _snap_superior(val, _CAMARA_FRONTAL_UNICOS)
            if snapped:
                filtros["camara_frontal_min"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Cámara — NNN mp / megapixeles (trasera) ───────────────────────────────
    for m in re.finditer(_pat_camara_kw, t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros.get("camara_min"):
            snapped = _snap_superior(val, _CAMARA_TRASERA_UNICOS)
            if snapped:
                filtros["camara_min"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Cámara — "camera NNN" / "câmera NNN" (sin mp) ────────────────────────
    for m in re.finditer(_pat_camara_kw2, t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros.get("camara_min") and val >= 8:
            snapped = _snap_superior(val, _CAMARA_TRASERA_UNICOS)
            if snapped:
                filtros["camara_min"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Batería — "capacidad / capacity / capacidade NNN" ────────────────────
    for m in re.finditer(_pat_capacidad, t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros["bateria_min"]:
            snapped = _snap_superior(val, _BATERIA_UNICOS) or str(val)
            filtros["bateria_min"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Almacenamiento — palabra clave + número ───────────────────────────────
    for m in re.finditer(_pat_storage_kw, t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros.get("almacenamiento") and val not in (4, 6, 8, 12, 16):
            snapped = _snap_superior(val, _STORAGE_UNICOS)
            if snapped:
                filtros["almacenamiento"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Almacenamiento con GB explícito (sin capturar vocab ya reconocidos) ───
    for m in re.finditer(r'\b(\d{2,4})\s*gb\b', t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros.get("almacenamiento") and val not in (4, 6, 8, 12, 16):
            snapped = _snap_superior(val, _STORAGE_UNICOS)
            if snapped:
                filtros["almacenamiento"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── RAM con número suelto ─────────────────────────────────────────────────
    # Soporta: "5gb ram", "5 gb de ram", "ram 5gb", "ram de 5gb"
    for m in re.finditer(
        r'\b(\d{1,2})\s*gb\s+(?:de\s+)?ram\b'     # "5gb ram"
        r'|\bram\s+(?:de\s+)?(\d{1,2})\s*gb\b',   # "ram 5gb"
        t, re.IGNORECASE
    ):
        val = int(m.group(1) or m.group(2))
        if not filtros.get("ram"):
            snapped = _snap_superior(val, _RAM_UNICOS)
            if snapped:
                filtros["ram"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    # ── Refresco — "NNN hz" sin operador ─────────────────────────────────────
    for m in re.finditer(r'\b(\d{2,3})\s*hz\b', t, re.IGNORECASE):
        val = int(m.group(1))
        if not filtros.get("refresco"):
            snapped = _snap_superior(val, _REFRESCO_UNICOS)
            if snapped:
                filtros["refresco"] = str(snapped)
        t = t[:m.start()] + " " * len(m.group()) + t[m.end():]

    return t


# ═══════════════════════════════════════════════════════════════════════════════
# INTÉRPRETE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def interpretar_consulta(termino: str, lang: str = "es") -> dict:
    """
    Traduce texto libre a un dict de filtros estructurados.
    Soporta idiomas: "es" (español), "en" (inglés), "pt" (portugués).
    Selecciona automáticamente el vocabulario semántico según el idioma.

    Implementa Opción C de Modelización Multilingüe:
    lexicón externo multilingüe enlazado a la ontología.

    - precio_modo: "rango" | "maximo" | "minimo" | None
      usado por sparql_engine para ordenar resultados.
    - Números de precio sin operador hacen snap al precio real inmediato superior.
    """
    # Selección de vocabulario según idioma (Opción C — lexicón externo)
    if lang == "en":
        vocab_activo    = VOCAB_SEMANTICO_EN
        ruido_activo    = PALABRAS_RUIDO_EN
        prefijos_neg    = PREFIJOS_NEGACION_EN
    elif lang == "pt":
        vocab_activo    = VOCAB_SEMANTICO_PT
        ruido_activo    = PALABRAS_RUIDO_PT
        prefijos_neg    = PREFIJOS_NEGACION_PT
    else:
        vocab_activo    = VOCAB_SEMANTICO
        ruido_activo    = PALABRAS_RUIDO
        prefijos_neg    = PREFIJOS_NEGACION

    t = _normalizar(termino)

    filtros: dict = {
        "gama": None, "so": None, "ram": None, "ram_min": None, "ram_max": None,
        "marca": None, "cpu": None, "nucleos": None,
        "pantalla": None, "pantalla_min": None, "pantalla_max": None,
        "refresco": None, "refresco_min": None,
        "bateria_min": None, "bateria_max": None,
        "carga_rapida": None, "carga_inalambrica": None,
        "almacenamiento": None, "microsd": None,
        "precio_min": None, "precio_max": None,
        "precio_modo": None,           # ← NUEVO: "rango" | "maximo" | "minimo"
        "red": None, "red_excl": None,
        "nfc": None, "bluetooth": None, "wifi": None,
        "sim": None, "sim_excl": None,
        "camara_min": None, "camara_max": None,
        "camara_frontal_min": None,
        "sensor": None, "sensor_excl": None,
        "resistencia": None, "resistencia_exacta": None, "resistencia_neg": None,
        "audio": None, "audio_neg": None,
        "anio_min": None, "anio_max": None,
        "texto_libre": termino,
        "sugerencias": [],
        "negaciones": [],
    }

    # Paso 0: extracción numérica (antes del vocab)
    t = _extraer_numericos(t, filtros, lang=lang)

    # Paso 1: detección exacta, frases largas primero
    # (usa vocab_activo según idioma — Opción C multilingüe)
    claves_ordenadas = sorted(vocab_activo.keys(), key=len, reverse=True)
    texto_marcado = t

    for clave in claves_ordenadas:
        if clave not in texto_marcado:
            continue
        cat, val, positivo = vocab_activo[clave]
        pos = texto_marcado.find(clave)
        esta_negado = not positivo
        for pref in prefijos_neg:
            ini = pos - len(pref)
            if ini >= 0 and texto_marcado[ini:pos] == pref:
                esta_negado = True
                break
        _aplicar_filtro(filtros, cat, val, esta_negado)
        texto_marcado = texto_marcado.replace(clave, " " * len(clave), 1)

    # Paso 2: fuzzy sobre lo que quedó
    for ruido in ruido_activo:
        texto_marcado = re.sub(rf'\b{re.escape(ruido)}\b', ' ', texto_marcado)
    texto_marcado = re.sub(r'\s+', ' ', texto_marcado).strip()

    if texto_marcado and len(texto_marcado) > 2:
        matches = _fuzzy_match_ngrams(texto_marcado, vocab=vocab_activo)
        for cat, val, pos_flag, clave_detectada, score in matches:
            esta_negado = not pos_flag
            if _aplicar_filtro(filtros, cat, val, esta_negado):
                etiqueta = val
                if cat == "resistencia":  etiqueta = f"resistencia ({val.upper()})"
                elif cat == "audio":       etiqueta = f"audio {val}"
                elif cat == "sensor":      etiqueta = val.replace("Sensor", "").strip()
                elif cat == "gama":        etiqueta = f"gama {val}"
                filtros["sugerencias"].append({
                    "original":     texto_marcado.strip(),
                    "interpretado": etiqueta,
                    "categoria":    cat,
                    "score":        round(score, 2),
                })

    return filtros