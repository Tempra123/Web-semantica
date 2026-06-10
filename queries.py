"""
queries.py — Las 80 consultas SPARQL de la ontología de celulares.
Cada categoría devuelve una lista de dicts con: id, titulo, descripcion, sparql, tipo
tipo: "SELECT" | "ASK"
"""

def get_all_queries(NS_URI):
    P = f"PREFIX : <{NS_URI}>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\n"

    return [
        # ── MARCA Y MODELO ──────────────────────────────────────────────
        {
            "id": 1, "categoria": "Marca y Modelo",
            "titulo": "¿Cuál es la marca del dispositivo?",
            "descripcion": "Lista todos los celulares con su marca.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?marca WHERE {
  ?cel a :Celular ;
       :marcaCelular ?marca .
}"""
        },
        {
            "id": 2, "categoria": "Marca y Modelo",
            "titulo": "¿Qué modelo es el dispositivo?",
            "descripcion": "Lista todos los celulares con su modelo.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?modelo WHERE {
  ?cel a :Celular ;
       :modeloCelular ?modelo .
}"""
        },
        {
            "id": 3, "categoria": "Marca y Modelo",
            "titulo": "¿En qué año fue lanzado?",
            "descripcion": "Muestra el año de lanzamiento de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?anio WHERE {
  ?cel a :Celular ;
       :anio ?anio .
}"""
        },
        {
            "id": 4, "categoria": "Marca y Modelo",
            "titulo": "¿A qué gama pertenece?",
            "descripcion": "Muestra la gama (Alta/Media/Baja) de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?gama WHERE {
  ?cel a :Celular ;
       :gama ?gama .
}"""
        },
        {
            "id": 5, "categoria": "Marca y Modelo",
            "titulo": "¿Qué celulares son de gama alta?",
            "descripcion": "Filtra los celulares de gama Alta.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?gama WHERE {
  ?cel a :Celular ;
       :gama ?gama .
  FILTER(str(?gama) = "Alta")
}"""
        },
        {
            "id": 6, "categoria": "Marca y Modelo",
            "titulo": "¿Qué celulares son de gama media?",
            "descripcion": "Filtra los celulares de gama Media.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?gama WHERE {
  ?cel a :Celular ;
       :gama ?gama .
  FILTER(str(?gama) = "Media")
}"""
        },
        {
            "id": 7, "categoria": "Marca y Modelo",
            "titulo": "¿Qué celulares son de gama baja?",
            "descripcion": "Filtra los celulares de gama Baja.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?gama WHERE {
  ?cel a :Celular ;
       :gama ?gama .
  FILTER(str(?gama) = "Baja")
}"""
        },
        {
            "id": 8, "categoria": "Marca y Modelo",
            "titulo": "¿Dos celulares en la misma gama?",
            "descripcion": "Encuentra pares de celulares que pertenecen a la misma gama.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?g ?c1 ?c2 WHERE {
  ?c1 :gama ?g .
  ?c2 :gama ?g .
  FILTER(?c1 != ?c2)
}
ORDER BY ?g ?c1 ?c2"""
        },
        {
            "id": 9, "categoria": "Marca y Modelo",
            "titulo": "¿Cuál celular es más reciente?",
            "descripcion": "Ordena los celulares por año de lanzamiento (más reciente primero).",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?anio WHERE {
  ?cel a :Celular ;
       :anio ?anio .
}
ORDER BY DESC(?anio)"""
        },
        {
            "id": 10, "categoria": "Marca y Modelo",
            "titulo": "¿Qué marcas producen más modelos por gama?",
            "descripcion": "Cuenta cuántos modelos tiene cada marca en cada gama.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?marca ?gama (COUNT(?cel) AS ?cantidad) WHERE {
  ?cel :marcaCelular ?marca ;
       :gama ?gama .
}
GROUP BY ?marca ?gama
ORDER BY ?marca DESC(?cantidad)"""
        },

        # ── PROCESADOR ──────────────────────────────────────────────────
        {
            "id": 11, "categoria": "Procesador",
            "titulo": "¿Cuál es la marca del procesador?",
            "descripcion": "Muestra el fabricante de CPU de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?marcaCPU WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :marcaCPU ?marcaCPU .
}"""
        },
        {
            "id": 12, "categoria": "Procesador",
            "titulo": "¿Cuál es el modelo del procesador?",
            "descripcion": "Muestra el modelo de CPU de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?modeloCPU WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :modeloCPU ?modeloCPU .
}"""
        },
        {
            "id": 13, "categoria": "Procesador",
            "titulo": "¿Cuántos núcleos tiene el procesador?",
            "descripcion": "Muestra el número de núcleos del procesador de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?nucleos WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :numeroNucleos ?nucleos .
}"""
        },
        {
            "id": 14, "categoria": "Procesador",
            "titulo": "¿Cuál es la frecuencia máxima del procesador?",
            "descripcion": "Lista la frecuencia máxima de CPU (ordenado de mayor a menor).",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?freq WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :frecuenciaMaxima ?freq .
}
ORDER BY DESC(?freq)"""
        },
        {
            "id": 15, "categoria": "Procesador",
            "titulo": "¿Qué celular tiene más núcleos?",
            "descripcion": "Compara los núcleos de procesador entre celulares.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?n WHERE {
  ?cel a :Celular ;
       :tieneProcesador ?cpu .
  ?cpu :numeroNucleos ?n .
}
ORDER BY DESC(?n)"""
        },
        {
            "id": 16, "categoria": "Procesador",
            "titulo": "¿Qué celular tiene la frecuencia más alta?",
            "descripcion": "Encuentra el celular con el procesador de mayor frecuencia.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?f WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :frecuenciaMaxima ?f .
}
ORDER BY DESC(?f)
LIMIT 1"""
        },
        {
            "id": 17, "categoria": "Procesador",
            "titulo": "¿Qué celulares usan procesador Qualcomm?",
            "descripcion": "Filtra celulares con CPU de la marca Qualcomm.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?marcaCPU WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :marcaCPU ?marcaCPU .
  FILTER(LCASE(str(?marcaCPU)) = "qualcomm")
}"""
        },
        {
            "id": 18, "categoria": "Procesador",
            "titulo": "¿Dos celulares usan el mismo procesador?",
            "descripcion": "Encuentra pares de celulares que comparten el mismo objeto procesador.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?c1 ?c2 ?cpu WHERE {
  ?c1 :tieneProcesador ?cpu .
  ?c2 :tieneProcesador ?cpu .
  FILTER(?c1 != ?c2)
}"""
        },
        {
            "id": 19, "categoria": "Procesador",
            "titulo": "¿Qué celulares comparten el mismo fabricante de CPU?",
            "descripcion": "Agrupa celulares por marca de procesador.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?marcaCPU (COUNT(?cel) AS ?cantidad) WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :marcaCPU ?marcaCPU .
}
GROUP BY ?marcaCPU"""
        },
        {
            "id": 20, "categoria": "Procesador",
            "titulo": "¿Cuál es el procesador más potente?",
            "descripcion": "Ordena por frecuencia y núcleos para encontrar el más potente.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?f ?n WHERE {
  ?cel :tieneProcesador ?cpu .
  ?cpu :frecuenciaMaxima ?f ;
       :numeroNucleos ?n .
}
ORDER BY DESC(?f) DESC(?n)
LIMIT 1"""
        },

        # ── MEMORIA ─────────────────────────────────────────────────────
        {
            "id": 21, "categoria": "Memoria",
            "titulo": "¿Cuánta RAM tiene el dispositivo?",
            "descripcion": "Muestra la RAM de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?ram WHERE {
  ?cel :tieneMemoria ?m .
  ?m :RAM ?ram .
}"""
        },
        {
            "id": 22, "categoria": "Memoria",
            "titulo": "¿Cuánto almacenamiento interno ofrece?",
            "descripcion": "Muestra el almacenamiento interno de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?alm WHERE {
  ?cel :tieneMemoria ?m .
  ?m :almacenamientoInterno ?alm .
}"""
        },
        {
            "id": 23, "categoria": "Memoria",
            "titulo": "¿El celular admite microSD?",
            "descripcion": "Muestra si cada celular admite tarjeta microSD.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (IF(str(?sd)="true","SÍ","NO") AS ?admiteMicroSD) WHERE {
  ?cel :tieneMemoria ?m .
  ?m :admiteMicroSD ?sd .
}"""
        },
        {
            "id": 24, "categoria": "Memoria",
            "titulo": "¿Qué celular tiene más RAM?",
            "descripcion": "Ordena los celulares por cantidad de RAM.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?ram WHERE {
  ?cel :tieneMemoria ?m .
  ?m :RAM ?ram .
}
ORDER BY DESC(?ram)"""
        },
        {
            "id": 25, "categoria": "Memoria",
            "titulo": "¿Qué celular tiene más almacenamiento?",
            "descripcion": "Encuentra el celular con mayor almacenamiento interno.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?alm WHERE {
  ?cel :tieneMemoria ?m .
  ?m :almacenamientoInterno ?alm .
}
ORDER BY DESC(?alm)
LIMIT 1"""
        },
        {
            "id": 26, "categoria": "Memoria",
            "titulo": "¿Cuáles celulares permiten expandir la memoria?",
            "descripcion": "Lista los celulares que aceptan microSD.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel :tieneMemoria ?m .
  ?m :admiteMicroSD ?val .
  FILTER(str(?val) = "true")
}"""
        },
        {
            "id": 27, "categoria": "Memoria",
            "titulo": "¿Qué modelos tienen más de 128 GB?",
            "descripcion": "Filtra celulares con almacenamiento interno mayor a 128 GB.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?a WHERE {
  ?cel :tieneMemoria ?m .
  ?m :almacenamientoInterno ?a .
  FILTER(?a > 128)
}"""
        },
        {
            "id": 28, "categoria": "Memoria",
            "titulo": "¿Qué celulares tienen 8 GB o más de RAM?",
            "descripcion": "Filtra celulares con 8 GB de RAM o más.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?r WHERE {
  ?cel :tieneMemoria ?m .
  ?m :RAM ?r .
  FILTER(?r >= 8)
}"""
        },
        {
            "id": 29, "categoria": "Memoria",
            "titulo": "¿El iPhone 14 admite microSD?",
            "descripcion": "Consulta booleana sobre si el iPhone 14 acepta microSD.",
            "tipo": "ASK",
            "sparql": P + """
ASK {
  :iPhone_14 :tieneMemoria ?m .
  ?m :admiteMicroSD ?val .
  FILTER(str(?val) = "true")
}"""
        },
        {
            "id": 30, "categoria": "Memoria",
            "titulo": "¿Qué marcas incluyen microSD?",
            "descripcion": "Cuenta cuántos celulares de cada marca aceptan microSD.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?marcaCelular (COUNT(DISTINCT ?cel) AS ?cantidad) WHERE {
  ?cel :marcaCelular ?marcaCelular ;
       :tieneMemoria ?m .
  ?m :admiteMicroSD ?micro .
  FILTER(str(?micro) = "true")
}
GROUP BY ?marcaCelular"""
        },

        # ── PANTALLA ─────────────────────────────────────────────────────
        {
            "id": 31, "categoria": "Pantalla",
            "titulo": "¿Qué tipo de pantalla tiene?",
            "descripcion": "Muestra el tipo de pantalla de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?tipo WHERE {
  ?cel :tienePantalla ?p .
  ?p :tipoPantalla ?tipo .
}"""
        },
        {
            "id": 32, "categoria": "Pantalla",
            "titulo": "¿Cuál es el tamaño de la pantalla?",
            "descripcion": "Lista el tamaño de pantalla (pulgadas) de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?tam WHERE {
  ?cel :tienePantalla ?p .
  ?p :tamanoPantalla ?tam .
}"""
        },
        {
            "id": 33, "categoria": "Pantalla",
            "titulo": "¿Cuál es la resolución de la pantalla?",
            "descripcion": "Muestra la resolución de pantalla de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?res WHERE {
  ?cel :tienePantalla ?p .
  ?p :resolucionPantalla ?res .
}"""
        },
        {
            "id": 34, "categoria": "Pantalla",
            "titulo": "¿Qué tasa de refresco ofrece?",
            "descripcion": "Muestra la tasa de refresco en Hz de cada pantalla.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?ref WHERE {
  ?cel :tienePantalla ?p .
  ?p :tasaRefresco ?ref .
}"""
        },
        {
            "id": 35, "categoria": "Pantalla",
            "titulo": "¿Qué celular tiene la pantalla más grande?",
            "descripcion": "Encuentra el celular con mayor tamaño de pantalla.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?t WHERE {
  ?cel :tienePantalla ?p .
  ?p :tamanoPantalla ?t .
}
ORDER BY DESC(?t)
LIMIT 1"""
        },
        {
            "id": 36, "categoria": "Pantalla",
            "titulo": "¿Qué celulares tienen pantalla AMOLED?",
            "descripcion": "Filtra celulares con tecnología AMOLED.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?tipo WHERE {
  ?cel :tienePantalla ?p .
  ?p :tipoPantalla ?tipo .
  FILTER(CONTAINS(UCASE(str(?tipo)), "AMOLED"))
}"""
        },
        {
            "id": 37, "categoria": "Pantalla",
            "titulo": "¿Qué celulares tienen 120 Hz?",
            "descripcion": "Filtra celulares con tasa de refresco de 120 Hz.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?ref WHERE {
  ?cel :tienePantalla ?p .
  ?p :tasaRefresco ?ref .
  FILTER(?ref = 120)
}"""
        },
        {
            "id": 38, "categoria": "Pantalla",
            "titulo": "¿Cuál tiene mejor pantalla por refresco?",
            "descripcion": "Ordena los celulares por tasa de refresco.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?ref ?tipo WHERE {
  ?cel :tienePantalla ?p .
  ?p :tasaRefresco ?ref .
  OPTIONAL { ?p :tipoPantalla ?tipo }
}
ORDER BY DESC(?ref)"""
        },

        # ── BATERÍA ──────────────────────────────────────────────────────
        {
            "id": 39, "categoria": "Batería",
            "titulo": "¿Cuál es la capacidad de la batería?",
            "descripcion": "Muestra la capacidad en mAh de la batería de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?cap WHERE {
  ?cel :tieneBateria ?b .
  ?b :capacidad ?cap .
}"""
        },
        {
            "id": 40, "categoria": "Batería",
            "titulo": "¿Tiene carga rápida?",
            "descripcion": "Lista los celulares que tienen carga rápida.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ("Tiene carga rápida" AS ?descripcion) WHERE {
  ?cel :tieneBateria ?b .
  ?b :cargaRapida ?val .
  FILTER(str(?val) = "true")
}"""
        },
        {
            "id": 41, "categoria": "Batería",
            "titulo": "¿Tiene carga inalámbrica?",
            "descripcion": "Lista los celulares con soporte de carga inalámbrica.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ("Tiene carga inalámbrica" AS ?descripcion) WHERE {
  ?cel :tieneBateria ?b .
  ?b :cargaInalambrica ?val .
  FILTER(str(?val) = "true")
}"""
        },
        {
            "id": 42, "categoria": "Batería",
            "titulo": "¿Qué celular tiene mayor batería?",
            "descripcion": "Encuentra el celular con mayor capacidad de batería.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?c WHERE {
  ?cel :tieneBateria ?b .
  ?b :capacidad ?c .
}
ORDER BY DESC(?c)
LIMIT 1"""
        },
        {
            "id": 43, "categoria": "Batería",
            "titulo": "¿Cuántos celulares incluyen carga inalámbrica?",
            "descripcion": "Cuenta el total de celulares con carga inalámbrica.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT (COUNT(?cel) AS ?total) WHERE {
  ?cel :tieneBateria ?b .
  ?b :cargaInalambrica ?val .
  FILTER(str(?val) = "true")
}"""
        },

        # ── CÁMARAS ──────────────────────────────────────────────────────
        {
            "id": 44, "categoria": "Cámaras",
            "titulo": "¿Cuál es la resolución de la cámara trasera?",
            "descripcion": "Muestra la resolución principal de la cámara trasera.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?res WHERE {
  ?cel :tieneCamaraTrasera ?c .
  ?c :resolucionPrincipal ?res .
}"""
        },
        {
            "id": 45, "categoria": "Cámaras",
            "titulo": "¿Cuántas cámaras traseras tiene?",
            "descripcion": "Muestra el número de cámaras traseras de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?num WHERE {
  ?cel :tieneCamaraTrasera ?c .
  ?c :numeroCamaras ?num .
}"""
        },
        {
            "id": 46, "categoria": "Cámaras",
            "titulo": "¿Cuál es la resolución de la cámara frontal?",
            "descripcion": "Muestra la resolución de la cámara frontal.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?res WHERE {
  ?cel :tieneCamaraFrontal ?c .
  ?c :resolucionFrontal ?res .
}"""
        },
        {
            "id": 47, "categoria": "Cámaras",
            "titulo": "¿Qué celular tiene más cámaras traseras?",
            "descripcion": "Encuentra el celular con mayor número de cámaras traseras.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (COUNT(?cam) AS ?totalCamaras) WHERE {
  ?cel :tieneCamaraTrasera ?cam .
}
GROUP BY ?cel
ORDER BY DESC(?totalCamaras)
LIMIT 1"""
        },
        {
            "id": 48, "categoria": "Cámaras",
            "titulo": "¿Qué celular tiene la cámara de mayor resolución?",
            "descripcion": "Encuentra la cámara principal de mayor resolución.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?r WHERE {
  ?cel :tieneCamaraTrasera ?c .
  ?c :resolucionPrincipal ?r .
}
ORDER BY DESC(?r)
LIMIT 1"""
        },
        {
            "id": 49, "categoria": "Cámaras",
            "titulo": "¿Qué celulares tienen más de una cámara frontal?",
            "descripcion": "Busca celulares con múltiples cámaras frontales.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (COUNT(?c) AS ?total) WHERE {
  ?cel :tieneCamaraFrontal ?c .
}
GROUP BY ?cel
HAVING(COUNT(?c) > 1)"""
        },
        {
            "id": 50, "categoria": "Cámaras",
            "titulo": "¿Cuáles son las resoluciones de todas las cámaras?",
            "descripcion": "Lista trasera y frontal de todos los celulares.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?resTrasera ?resFrontal WHERE {
  OPTIONAL { ?cel :tieneCamaraTrasera ?ct . ?ct :resolucionPrincipal ?resTrasera . }
  OPTIONAL { ?cel :tieneCamaraFrontal ?cf . ?cf :resolucionFrontal ?resFrontal . }
  FILTER(BOUND(?resTrasera) || BOUND(?resFrontal))
}"""
        },

        # ── CONECTIVIDAD ─────────────────────────────────────────────────
        {
            "id": 51, "categoria": "Conectividad",
            "titulo": "¿Este celular tiene 4G?",
            "descripcion": "Verifica si el Huawei Nova 11 soporta red 4G.",
            "tipo": "ASK",
            "sparql": P + """
ASK {
  :Huawei_Nova_11 :tieneRedMovil ?r .
  ?r :tipoRedMovil ?tipo .
  FILTER regex(STR(?tipo), "4G")
}"""
        },
        {
            "id": 52, "categoria": "Conectividad",
            "titulo": "¿El iPhone 14 tiene 5G?",
            "descripcion": "Verifica si el iPhone 14 soporta red 5G.",
            "tipo": "ASK",
            "sparql": P + """
ASK {
  :iPhone_14 :tieneRedMovil ?r .
  ?r :tipoRedMovil ?tipo .
  FILTER regex(STR(?tipo), "5G")
}"""
        },
        {
            "id": 53, "categoria": "Conectividad",
            "titulo": "¿El iPhone 14 tiene Wi-Fi?",
            "descripcion": "Verifica si el iPhone 14 tiene conectividad WiFi.",
            "tipo": "ASK",
            "sparql": P + """
ASK {
  :iPhone_14 :tieneRedInalambrica ?r .
  ?r :tipoRedInalambrica ?tipo .
  FILTER regex(STR(?tipo), "WiFi")
}"""
        },
        {
            "id": 54, "categoria": "Conectividad",
            "titulo": "¿Qué celulares tienen Bluetooth?",
            "descripcion": "Lista los celulares con conectividad Bluetooth.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (GROUP_CONCAT(DISTINCT ?tipo; separator=", ") AS ?conectividad) WHERE {
  ?cel a :Celular .
  ?cel :tieneRedInalambrica ?r .
  ?r :tipoRedInalambrica ?tipo .
  FILTER regex(?tipo, "Bluetooth")
}
GROUP BY ?cel"""
        },
        {
            "id": 55, "categoria": "Conectividad",
            "titulo": "¿Qué celulares tienen NFC?",
            "descripcion": "Lista los celulares con soporte NFC.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (GROUP_CONCAT(DISTINCT ?tipo; separator=", ") AS ?conectividad) WHERE {
  ?cel a :Celular .
  ?cel :tieneRedInalambrica ?r .
  ?r :tipoRedInalambrica ?tipo .
  FILTER(?tipo = "NFC")
}
GROUP BY ?cel"""
        },
        {
            "id": 56, "categoria": "Conectividad",
            "titulo": "¿El iPhone 14 es Dual SIM?",
            "descripcion": "Verifica si el iPhone 14 es compatible con Dual SIM.",
            "tipo": "ASK",
            "sparql": P + """
ASK {
  :iPhone_14 :tieneTipoSIM :DualSIM .
}"""
        },
        {
            "id": 57, "categoria": "Conectividad",
            "titulo": "¿Qué celulares soportan eSIM?",
            "descripcion": "Lista los celulares compatibles con eSIM.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (GROUP_CONCAT(DISTINCT ?sim; separator=", ") AS ?tiposSIM) WHERE {
  ?cel :tieneTipoSIM :eSIM .
  ?cel :tieneTipoSIM ?sim .
}
GROUP BY ?cel"""
        },
        {
            "id": 58, "categoria": "Conectividad",
            "titulo": "¿Cuáles celulares no tienen NFC?",
            "descripcion": "Lista los celulares que NO tienen NFC.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel a :Celular .
  FILTER NOT EXISTS {
    ?cel :tieneRedInalambrica ?r2 .
    ?r2 :tipoRedInalambrica "NFC" .
  }
}"""
        },
        {
            "id": 59, "categoria": "Conectividad",
            "titulo": "¿Qué celulares tienen 5G?",
            "descripcion": "Filtra todos los celulares con soporte 5G.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?tipo WHERE {
  ?cel :tieneRedMovil ?r .
  ?r :tipoRedMovil ?tipo .
  FILTER regex(STR(?tipo), "5G")
}"""
        },
        {
            "id": 60, "categoria": "Conectividad",
            "titulo": "¿Qué modelo ofrece más conectividad?",
            "descripcion": "Cuenta el total de tecnologías de conexión por celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (COUNT(DISTINCT ?tipo) AS ?total)
       (GROUP_CONCAT(DISTINCT ?tipo; separator=", ") AS ?conectividad)
WHERE {
  ?cel a :Celular .
  {
    ?cel :tieneRedInalambrica ?red .
    ?red :tipoRedInalambrica ?tipo .
  }
  UNION
  {
    ?cel :tieneRedMovil ?redM .
    ?redM :tipoRedMovil ?tipo .
  }
}
GROUP BY ?cel
ORDER BY DESC(?total)
LIMIT 1"""
        },
        {
            "id": 61, "categoria": "Conectividad",
            "titulo": "¿Qué celular tiene más conexiones inalámbricas?",
            "descripcion": "Cuenta tecnologías inalámbricas por celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (COUNT(DISTINCT ?tipo) AS ?total)
       (GROUP_CONCAT(DISTINCT ?tipo; separator=", ") AS ?tecnologias)
WHERE {
  ?cel a :Celular .
  ?cel :tieneRedInalambrica ?r .
  ?r :tipoRedInalambrica ?tipo .
}
GROUP BY ?cel
ORDER BY DESC(?total)
LIMIT 1"""
        },
        {
            "id": 62, "categoria": "Conectividad",
            "titulo": "¿Cuántas tecnologías de conexión tiene cada celular?",
            "descripcion": "Cuenta conectividad total (inalámbrica + móvil) de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (COUNT(DISTINCT ?tipo) AS ?total) WHERE {
  ?cel a :Celular .
  {
    ?cel :tieneRedInalambrica ?r .
    ?r :tipoRedInalambrica ?tipo .
  }
  UNION
  {
    ?cel :tieneRedMovil ?rm .
    ?rm :tipoRedMovil ?tipo .
  }
}
GROUP BY ?cel
ORDER BY DESC(?total)"""
        },
        {
            "id": 63, "categoria": "Conectividad",
            "titulo": "¿Hay celulares con 5G pero sin NFC?",
            "descripcion": "Filtra celulares con 5G que no tienen NFC.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel a :Celular .
  ?cel :tieneRedMovil ?rm .
  ?rm :tipoRedMovil "5G" .
  FILTER NOT EXISTS {
    ?cel :tieneRedInalambrica ?r .
    ?r :tipoRedInalambrica "NFC" .
  }
}"""
        },
        {
            "id": 64, "categoria": "Conectividad",
            "titulo": "¿Qué modelos incluyen Dual SIM y eSIM?",
            "descripcion": "Busca celulares que tengan ambos: Dual SIM y eSIM.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel :tieneTipoSIM :DualSIM .
  ?cel :tieneTipoSIM :eSIM .
}"""
        },

        # ── CARACTERÍSTICAS ESPECIALES ───────────────────────────────────
        {
            "id": 65, "categoria": "Características Especiales",
            "titulo": "¿Tiene lector de huellas?",
            "descripcion": "Lista los celulares con sensor de huella dactilar.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel :tieneSensor :SensorHuella .
}"""
        },
        {
            "id": 66, "categoria": "Características Especiales",
            "titulo": "¿Tiene reconocimiento facial?",
            "descripcion": "Lista los celulares con sensor de reconocimiento facial.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel :tieneSensor :SensorFacial .
}"""
        },
        {
            "id": 67, "categoria": "Características Especiales",
            "titulo": "¿Es resistente al agua (IP67/IP68)?",
            "descripcion": "Lista celulares con certificación de resistencia al agua.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?cert ?nombre WHERE {
  ?cel :tieneResistencia ?r .
  ?r :certificacion ?cert .
  OPTIONAL { ?r :nombreResistencia ?nombre }
  FILTER(?cert = "IP67" || ?cert = "IP68")
}"""
        },
        {
            "id": 68, "categoria": "Características Especiales",
            "titulo": "¿El dispositivo tiene audio estéreo?",
            "descripcion": "Lista los celulares con sistema de audio estéreo.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel a :Celular .
  ?cel :tieneAudio :AudioStereo .
}"""
        },
        {
            "id": 69, "categoria": "Características Especiales",
            "titulo": "¿Cuáles tienen huella Y reconocimiento facial?",
            "descripcion": "Celulares que combinan ambos sensores biométricos.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel :tieneSensor :SensorHuella ;
       :tieneSensor :SensorFacial .
}"""
        },
        {
            "id": 70, "categoria": "Características Especiales",
            "titulo": "¿Cuáles NO tienen audio estéreo?",
            "descripcion": "Lista los celulares sin audio estéreo.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel WHERE {
  ?cel a :Celular .
  FILTER NOT EXISTS {
    ?cel :tieneAudio :AudioStereo .
  }
}"""
        },
        {
            "id": 71, "categoria": "Características Especiales",
            "titulo": "¿Qué modelos tienen certificación de resistencia al agua?",
            "descripcion": "Lista todos los celulares con certificación IP.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?cert ?nombre WHERE {
  ?cel :tieneResistencia ?res .
  ?res :certificacion ?cert .
  OPTIONAL { ?res :nombreResistencia ?nombre }
}"""
        },
        {
            "id": 72, "categoria": "Características Especiales",
            "titulo": "¿Qué celular tiene más funciones especiales?",
            "descripcion": "Cuenta sensores + resistencia + audio por celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel (COUNT(?f) AS ?total) WHERE {
  {  ?cel :tieneSensor ?f . }
  UNION { ?cel :tieneResistencia ?f . }
  UNION { ?cel :tieneAudio ?f . }
}
GROUP BY ?cel
ORDER BY DESC(?total)
LIMIT 1"""
        },
        {
            "id": 73, "categoria": "Características Especiales",
            "titulo": "¿El Xiaomi Redmi Note 12 tiene huella bajo pantalla?",
            "descripcion": "Consulta booleana sobre sensor de huella del Redmi Note 12.",
            "tipo": "ASK",
            "sparql": P + """
ASK {
  :Xiaomi_Redmi_Note_12 :tieneSensor :SensorHuella .
}"""
        },
        {
            "id": 74, "categoria": "Características Especiales",
            "titulo": "¿Qué marcas incluyen más funciones especiales?",
            "descripcion": "Promedio de funciones especiales por marca.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?marca (COUNT(?f) AS ?total) WHERE {
  ?cel :marcaCelular ?marca .
  {  ?cel :tieneSensor ?f . }
  UNION { ?cel :tieneResistencia ?f . }
  UNION { ?cel :tieneAudio ?f . }
}
GROUP BY ?marca
ORDER BY DESC(?total)"""
        },

        # ── SISTEMA OPERATIVO ─────────────────────────────────────────────
        {
            "id": 75, "categoria": "Sistema Operativo",
            "titulo": "¿Qué sistema operativo usa el celular?",
            "descripcion": "Muestra el sistema operativo de cada celular.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?cel ?so WHERE {
  ?cel a :Celular .
  {
    ?cel :tieneSistemaOperativo ?soObj .
    ?soObj :nombreSO ?so .
  } UNION {
    ?cel :tieneSistemaOperativo ?so .
    FILTER(isLiteral(?so))
  }
}"""
        },

        # ── PRECIO ───────────────────────────────────────────────────────
        {
            "id": 76, "categoria": "Precio",
            "titulo": "¿Cuáles son todos los celulares y su precio?",
            "descripcion": "Lista todos los celulares con su precio en dólares.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?celular ?precio WHERE {
  ?celular a :Celular ;
           :precio ?precio .
}
ORDER BY ?precio"""
        },
        {
            "id": 77, "categoria": "Precio",
            "titulo": "¿Qué celulares cuestan más de $700?",
            "descripcion": "Filtra celulares con precio superior a 700 USD.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?celular ?precio WHERE {
  ?celular a :Celular ;
           :precio ?precio .
  FILTER(?precio > 700)
}
ORDER BY DESC(?precio)"""
        },
        {
            "id": 78, "categoria": "Precio",
            "titulo": "¿Qué celulares cuestan menos de $300?",
            "descripcion": "Filtra celulares con precio inferior a 300 USD.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT ?celular ?precio WHERE {
  ?celular a :Celular ;
           :precio ?precio .
  FILTER(?precio < 300)
}
ORDER BY ?precio"""
        },
        {
            "id": 79, "categoria": "Precio",
            "titulo": "¿Cuál es el más caro y el más barato?",
            "descripcion": "Muestra el precio mínimo y máximo de la ontología.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT (MIN(?precio) AS ?precioMin) (MAX(?precio) AS ?precioMax) WHERE {
  ?celular a :Celular ;
           :precio ?precio .
}"""
        },
        {
            "id": 80, "categoria": "Precio",
            "titulo": "¿Cuál es el precio promedio?",
            "descripcion": "Calcula el precio promedio de todos los celulares.",
            "tipo": "SELECT",
            "sparql": P + """
SELECT (AVG(?precio) AS ?precioPromedio) (COUNT(?cel) AS ?total) WHERE {
  ?cel a :Celular ;
       :precio ?precio .
}"""
        },
    ]


CATEGORIAS = [
    "Marca y Modelo",
    "Procesador",
    "Memoria",
    "Pantalla",
    "Batería",
    "Cámaras",
    "Conectividad",
    "Características Especiales",
    "Sistema Operativo",
    "Precio",
]