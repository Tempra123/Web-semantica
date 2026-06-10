// ── app.js — SPA unificado con hash routing ───────────────────────────────────

// ═══════════════════════════════════════════════════════════════════
// 0. INTERNACIONALIZACIÓN (i18n) — ES / EN / PT
// ═══════════════════════════════════════════════════════════════════

const I18N = {
  es: {
    nav_buscador:   "🔍 Buscador",
    nav_consultas:  "⚡ 80 Consultas SPARQL",
    nav_dbpedia:    "🌐 DBpedia",
    header_buscador_h1:   "Buscador Semántico<br><span>de Teléfonos Celulares</span>",
    header_consultas_h1:  "80 Consultas SPARQL<br><span>Ontología de Celulares</span>",
    header_dbpedia_h1:    "DBpedia <br>",
    page_buscador:  "Buscador Semántico · Celulares",
    page_consultas: "80 Consultas SPARQL · Celulares",
    page_dbpedia:   "DBpedia Online · Celulares",
    search_placeholder: 'Ej: "celulares baratos", "Android gama alta", "Samsung 5G"...',
    btn_buscar:     "Buscar",
    stat_celulares: "Celulares",
    stat_clases:    "Clases OWL",
    stat_tripletas: "Tripletas RDF",
    stat_consultas: "Consultas SPARQL",
    sug_label:      "Prueba:",
    sug_chips: ["celulares baratos", "Android gama alta", "Samsung 5G", "iPhone", "Xiaomi RAM 8", "batería 5000"],
    empty_init_h3:  "Ingresá un término y presioná Buscar",
    empty_init_p:   "O usá una de las sugerencias",
    empty_h3:       "Sin resultados",
    empty_p:        "Probá con otro término o cambiá los filtros",
    results_count:  (n) => `${n} resultado${n !== 1 ? "s" : ""}`,
    detected:       "🧠 Detectado:",
    gama_alta:      "Gama Alta",
    gama_media:     "Gama Media",
    gama_baja:      "Gama Baja",
    loading_ontologia:  "Consultando ontología",
    loading_dbpedia:    "Consultando DBpedia",
    loading_specs:      "Cargando especificaciones",
    error_conexion_h3:  "Error de conexión",
    error_conexion_p:   "Verificá que Flask esté corriendo en el puerto 5000",
    error_dbpedia_h3:   "Error al conectar con DBpedia",
    dbp_connected:      "Conectado a DBpedia SPARQL Endpoint",
    dbp_search_placeholder: 'Ej: "iPhone", "Samsung Galaxy", "Xiaomi"...',
    dbp_btn_buscar:     "Buscar en DBpedia",
    dbp_empty_h3:       "Buscá celulares en DBpedia",
    dbp_empty_p:        "Los resultados vienen directamente del endpoint SPARQL de DBpedia",
    dbp_sin_resultados_h3: "Sin resultados en DBpedia",
    dbp_sin_resultados_p:  "Intentá con otro término o verificá tu conexión a internet",
    dbp_results_count:  (n) => `${n} resultado${n !== 1 ? "s" : ""} en DBpedia`,
    btn_agregar:        "➕ Agregar a ontología",
    btn_agregado:       "✓ Agregado",
    btn_ya_existe:      "✓ Ya existe",
    btn_consultando:    "⏳ Consultando DBpedia...",
    error_desconocido:  "Error: desconocido",
    error_flask:        "Error de conexión con Flask.",
    modal_detalle:      "Detalle del dispositivo",
    timeout_error:      "⏱ El servidor tardó demasiado. Verificá que Flask esté corriendo.",
    cat_todas:          "Todas",
    cats_sidebar:       "Categorías",
    query_search_ph:    "Buscar entre las 80 consultas...",
    executing:          "Ejecutando consulta...",
    rows_returned:      (n) => `${n} fila${n !== 1 ? "s" : ""} devuelta${n !== 1 ? "s" : ""}`,
    no_results_query:   "La consulta no devolvió resultados en esta ontología.",
    btn_ver_sparql:     "{ } Ver SPARQL",
    btn_cerrar:         "✕ Cerrar",
    footer:             "Buscador Semántico · Ontología de Teléfonos Celulares · Web Semánticas 2026",
    nav_multilang:      "🗣 Ontología Multilingüe",
    header_multilang_h1: "Ontología Multilingüe<br>",
    page_multilang:     "Ontología Multilingüe · Celulares",
    ml_clases:          "📦 Clases OWL",
    ml_props_obj:       "🔗 Propiedades de Objeto",
    ml_props_dato:      "🏷 Propiedades de Dato",
    ml_badge_texto:    "Representación Semántica Multilingüe · rdfs:label con @lang",
    ml_lang_label:     "Consultar ontología en:",
    ml_consultando:    "Consultando ontología",
    ml_clases_stat:    "Clases",
    ml_props_obj_stat: "Prop. Objeto",
    ml_props_dato_stat:"Prop. Dato",
    ml_indiv_stat:     "Individuos",
    ml_titulo_clases:  "📦 Clases OWL",
    ml_titulo_obj:     "🔗 Propiedades de Objeto",
    ml_titulo_dato:    "🏷 Propiedades de Dato",
    ml_titulo_indiv:   "🧩 Individuos",
    ml_ver_sparql:     "{ } Ver SPARQL",
    tag_local:              "Ontología",
    tag_local_tooltip:      "Resultado de la ontología local OWL",
    results_count_combined: (l, d) => `${l} local${l!==1?"es":""} + ${d} DBpedia`,
    dbp_section_label:      "Resultados de DBpedia",
    label_frontal:          "frontal",
    grupo_general:          "General",
    grupo_procesador:       "Procesador",
    grupo_memoria:          "Memoria",
    grupo_bateria:          "Batería",
    grupo_pantalla:         "Pantalla",
    grupo_camara_trasera:   "Cámara Trasera",
    grupo_camara_frontal:   "Cámara Frontal",
    grupo_so:               "Sistema Operativo",
    grupo_audio:            "Audio",
    grupo_red_movil:        "Red Móvil",
    grupo_conectividad:     "Conectividad Inalámbrica",
    grupo_sensores:         "Sensores",
    grupo_resistencia:      "Resistencia",
    grupo_sim:              "Tipo de SIM",
    prop_marca:             "Marca",
    prop_modelo:            "Modelo",
    prop_gama:              "Gama",
    prop_precio:            "Precio (USD)",
    prop_anio:              "Año",
    prop_fabricante_cpu:    "Fabricante CPU",
    prop_modelo_cpu:        "Modelo CPU",
    prop_nucleos:           "Núcleos",
    prop_frecuencia_max:    "Frecuencia Máx. (GHz)",
    prop_ram:               "RAM (GB)",
    prop_almacenamiento:    "Almacenamiento (GB)",
    prop_microsd:           "MicroSD",
    prop_capacidad:         "Capacidad (mAh)",
    prop_carga_rapida:      "Carga Rápida",
    prop_carga_inalambrica: "Carga Inalámbrica",
    prop_tipo_pantalla:     "Tipo",
    prop_tamano_pantalla:   "Tamaño (pulg.)",
    prop_tasa_refresco:     "Tasa Refresco (Hz)",
    prop_resolucion:        "Resolución",
    prop_resolucion_principal: "Resolución Principal (MP)",
    prop_num_camaras:       "Número de Cámaras",
    prop_resolucion_frontal:"Resolución Frontal (MP)",
    prop_so:                "Sistema Operativo",
    prop_salida_audio:      "Salida de Audio",
    prop_red_movil:         "Red Móvil",
    prop_tecnologia:        "Tecnología",
    prop_sensor:            "Sensor",
    prop_certificacion_ip:  "Certificación IP",
    prop_descripcion:       "Descripción",
    bool_true:              "✓ Sí",
    bool_false:             "✗ No",
    // Claves faltantes
    prop_tipo_sim:          "Tipo",
    prop_label_red:         "Etiqueta",
    prop_fuente_dbp:        "Fuente DBpedia",
    prop_enlace_dbp:        "Enlace DBpedia",
    prop_imagen_dbp:        "Imagen DBpedia",
  },
  en: {
    nav_buscador:   "🔍 Search",
    nav_consultas:  "⚡ 80 SPARQL Queries",
    nav_dbpedia:    "🌐 DBpedia",
    header_buscador_h1:   "Semantic Search<br><span>for Mobile Phones</span>",
    header_consultas_h1:  "80 SPARQL Queries<br><span>Cell Phone Ontology</span>",
    header_dbpedia_h1:    "DBpedia Online<br>",
    page_buscador:  "Semantic Search · Phones",
    page_consultas: "80 SPARQL Queries · Phones",
    page_dbpedia:   "DBpedia Online · Phones",
    search_placeholder: 'e.g. "cheap phones", "high-end Android", "Samsung 5G"...',
    btn_buscar:     "Search",
    stat_celulares: "Phones",
    stat_clases:    "OWL Classes",
    stat_tripletas: "RDF Triples",
    stat_consultas: "SPARQL Queries",
    sug_label:      "Try:",
    sug_chips: ["cheap phones", "high-end Android", "Samsung 5G", "iPhone iOS", "8GB RAM", "cheap Samsung"],
    empty_init_h3:  "Enter a term and press Search",
    empty_init_p:   "Or use one of the suggestions",
    empty_h3:       "No results",
    empty_p:        "Try another term or change the filters",
    results_count:  (n) => `${n} result${n !== 1 ? "s" : ""}`,
    detected:       "🧠 Detected:",
    gama_alta:      "High-End",
    gama_media:     "Mid-Range",
    gama_baja:      "Budget",
    loading_ontologia:  "Querying ontology",
    loading_dbpedia:    "Querying DBpedia",
    loading_specs:      "Loading specs",
    error_conexion_h3:  "Connection error",
    error_conexion_p:   "Make sure Flask is running on port 5000",
    error_dbpedia_h3:   "Error connecting to DBpedia",
    dbp_connected:      "Connected to DBpedia SPARQL Endpoint",
    dbp_search_placeholder: 'e.g. "iPhone", "Samsung Galaxy", "Xiaomi"...',
    dbp_btn_buscar:     "Search DBpedia",
    dbp_empty_h3:       "Search phones in DBpedia",
    dbp_empty_p:        "Results come directly from the DBpedia SPARQL endpoint",
    dbp_sin_resultados_h3: "No results in DBpedia",
    dbp_sin_resultados_p:  "Try a different term or check your internet connection",
    dbp_results_count:  (n) => `${n} result${n !== 1 ? "s" : ""} in DBpedia`,
    btn_agregar:        "➕ Add to ontology",
    btn_agregado:       "✓ Added",
    btn_ya_existe:      "✓ Already exists",
    btn_consultando:    "⏳ Querying DBpedia...",
    error_desconocido:  "Error: unknown",
    error_flask:        "Flask connection error.",
    modal_detalle:      "Device detail",
    timeout_error:      "⏱ Server took too long. Make sure Flask is running.",
    cat_todas:          "All",
    cats_sidebar:       "Categories",
    query_search_ph:    "Search among the 80 queries...",
    executing:          "Running query...",
    rows_returned:      (n) => `${n} row${n !== 1 ? "s" : ""} returned`,
    no_results_query:   "The query returned no results in this ontology.",
    btn_ver_sparql:     "{ } View SPARQL",
    btn_cerrar:         "✕ Close",
    footer:             "Semantic Search · Cell Phone Ontology · Semantic Web 2026",
    nav_multilang:      "🗣 Multilingual Ontology",
    header_multilang_h1: "Multilingual Ontology<br>",
    page_multilang:     "Multilingual Ontology · Phones",
    ml_clases:          "📦 OWL Classes",
    ml_props_obj:       "🔗 Object Properties",
    ml_props_dato:      "🏷 Data Properties",
    ml_badge_texto:    "Multilingual Semantic Representation · rdfs:label with @lang",
    ml_lang_label:     "Query ontology in:",
    ml_consultando:    "Querying ontology",
    ml_clases_stat:    "Classes",
    ml_props_obj_stat: "Obj. Properties",
    ml_props_dato_stat:"Data Properties",
    ml_indiv_stat:     "Individuals",
    ml_titulo_clases:  "📦 OWL Classes",
    ml_titulo_obj:     "🔗 Object Properties",
    ml_titulo_dato:    "🏷 Data Properties",
    ml_titulo_indiv:   "🧩 Individuals",
    ml_ver_sparql:     "{ } View SPARQL",
    tag_local:              "Ontology",
    tag_local_tooltip:      "Result from local OWL ontology",
    results_count_combined: (l, d) => `${l} local + ${d} DBpedia`,
    dbp_section_label:      "DBpedia Results",
    label_frontal:          "front",
    grupo_general:          "General",
    grupo_procesador:       "Processor",
    grupo_memoria:          "Memory",
    grupo_bateria:          "Battery",
    grupo_pantalla:         "Display",
    grupo_camara_trasera:   "Rear Camera",
    grupo_camara_frontal:   "Front Camera",
    grupo_so:               "Operating System",
    grupo_audio:            "Audio",
    grupo_red_movil:        "Mobile Network",
    grupo_conectividad:     "Wireless Connectivity",
    grupo_sensores:         "Sensors",
    grupo_resistencia:      "Resistance",
    grupo_sim:              "SIM Type",
    prop_marca:             "Brand",
    prop_modelo:            "Model",
    prop_gama:              "Tier",
    prop_precio:            "Price (USD)",
    prop_anio:              "Year",
    prop_fabricante_cpu:    "CPU Manufacturer",
    prop_modelo_cpu:        "CPU Model",
    prop_nucleos:           "Cores",
    prop_frecuencia_max:    "Max Freq. (GHz)",
    prop_ram:               "RAM (GB)",
    prop_almacenamiento:    "Storage (GB)",
    prop_microsd:           "MicroSD",
    prop_capacidad:         "Capacity (mAh)",
    prop_carga_rapida:      "Fast Charging",
    prop_carga_inalambrica: "Wireless Charging",
    prop_tipo_pantalla:     "Type",
    prop_tamano_pantalla:   "Size (in.)",
    prop_tasa_refresco:     "Refresh Rate (Hz)",
    prop_resolucion:        "Resolution",
    prop_resolucion_principal: "Main Resolution (MP)",
    prop_num_camaras:       "Number of Cameras",
    prop_resolucion_frontal:"Front Resolution (MP)",
    prop_so:                "Operating System",
    prop_salida_audio:      "Audio Output",
    prop_red_movil:         "Mobile Network",
    prop_tecnologia:        "Technology",
    prop_sensor:            "Sensor",
    prop_certificacion_ip:  "IP Certification",
    prop_descripcion:       "Description",
    bool_true:              "✓ Yes",
    bool_false:             "✗ No",
    // Missing keys
    prop_tipo_sim:          "Type",
    prop_label_red:         "Label",
    prop_fuente_dbp:        "DBpedia Source",
    prop_enlace_dbp:        "DBpedia Link",
    prop_imagen_dbp:        "DBpedia Image",
  },
  pt: {
    nav_buscador:   "🔍 Busca",
    nav_consultas:  "⚡ 80 Consultas SPARQL",
    nav_dbpedia:    "🌐 DBpedia",
    header_buscador_h1:   "Busca Semântica<br><span>de Telefones Celulares</span>",
    header_consultas_h1:  "80 Consultas SPARQL<br><span>Ontologia de Celulares</span>",
    header_dbpedia_h1:    "DBpedia Online<br>",
    page_buscador:  "Busca Semântica · Celulares",
    page_consultas: "80 Consultas SPARQL · Celulares",
    page_dbpedia:   "DBpedia Online · Celulares",
    search_placeholder: 'Ex: "celulares baratos", "Android top de linha", "Samsung 5G"...',
    btn_buscar:     "Buscar",
    stat_celulares: "Celulares",
    stat_clases:    "Classes OWL",
    stat_tripletas: "Triplas RDF",
    stat_consultas: "Consultas SPARQL",
    sug_label:      "Tente:",
    sug_chips: ["celulares baratos", "Android top de linha", "Samsung 5G", "iPhone iOS", "8GB RAM", "Samsung barato"],
    empty_init_h3:  "Digite um termo e pressione Buscar",
    empty_init_p:   "Ou use uma das sugestões",
    empty_h3:       "Sem resultados",
    empty_p:        "Tente outro termo ou mude os filtros",
    results_count:  (n) => `${n} resultado${n !== 1 ? "s" : ""}`,
    detected:       "🧠 Detectado:",
    gama_alta:      "Top de Linha",
    gama_media:     "Intermediário",
    gama_baja:      "Entrada",
    loading_ontologia:  "Consultando ontologia",
    loading_dbpedia:    "Consultando DBpedia",
    loading_specs:      "Carregando especificações",
    error_conexion_h3:  "Erro de conexão",
    error_conexion_p:   "Verifique se o Flask está rodando na porta 5000",
    error_dbpedia_h3:   "Erro ao conectar ao DBpedia",
    dbp_connected:      "Conectado ao DBpedia SPARQL Endpoint",
    dbp_search_placeholder: 'Ex: "iPhone", "Samsung Galaxy", "Xiaomi"...',
    dbp_btn_buscar:     "Buscar no DBpedia",
    dbp_empty_h3:       "Pesquise celulares no DBpedia",
    dbp_empty_p:        "Os resultados vêm diretamente do endpoint SPARQL do DBpedia",
    dbp_sin_resultados_h3: "Sem resultados no DBpedia",
    dbp_sin_resultados_p:  "Tente outro termo ou verifique sua conexão à internet",
    dbp_results_count:  (n) => `${n} resultado${n !== 1 ? "s" : ""} no DBpedia`,
    btn_agregar:        "➕ Adicionar à ontologia",
    btn_agregado:       "✓ Adicionado",
    btn_ya_existe:      "✓ Já existe",
    btn_consultando:    "⏳ Consultando DBpedia...",
    error_desconocido:  "Erro: desconhecido",
    error_flask:        "Erro de conexão com Flask.",
    modal_detalle:      "Detalhe do dispositivo",
    timeout_error:      "⏱ Servidor demorou demais. Verifique se o Flask está rodando.",
    cat_todas:          "Todas",
    cats_sidebar:       "Categorias",
    query_search_ph:    "Buscar entre as 80 consultas...",
    executing:          "Executando consulta...",
    rows_returned:      (n) => `${n} linha${n !== 1 ? "s" : ""} retornada${n !== 1 ? "s" : ""}`,
    no_results_query:   "A consulta não retornou resultados nesta ontologia.",
    btn_ver_sparql:     "{ } Ver SPARQL",
    btn_cerrar:         "✕ Fechar",
    footer:             "Busca Semântica · Ontologia de Telefones Celulares · Web Semântica 2026",
    nav_multilang:      "🗣 Ontologia Multilíngue",
    header_multilang_h1: "Ontologia Multilíngue<br>",
    page_multilang:     "Ontologia Multilíngue · Celulares",
    ml_clases:          "📦 Classes OWL",
    ml_props_obj:       "🔗 Propriedades de Objeto",
    ml_props_dato:      "🏷 Propriedades de Dado",
    ml_badge_texto:    "Representação Semântica Multilíngue · rdfs:label com @lang",
    ml_lang_label:     "Consultar ontologia em:",
    ml_consultando:    "Consultando ontologia",
    ml_clases_stat:    "Classes",
    ml_props_obj_stat: "Prop. Objeto",
    ml_props_dato_stat:"Prop. Dado",
    ml_indiv_stat:     "Indivíduos",
    ml_titulo_clases:  "📦 Classes OWL",
    ml_titulo_obj:     "🔗 Propriedades de Objeto",
    ml_titulo_dato:    "🏷 Propriedades de Dado",
    ml_titulo_indiv:   "🧩 Indivíduos",
    ml_ver_sparql:     "{ } Ver SPARQL",
    tag_local:              "Ontologia",
    tag_local_tooltip:      "Resultado da ontologia local OWL",
    results_count_combined: (l, d) => `${l} local${l!==1?"is":""} + ${d} DBpedia`,
    dbp_section_label:      "Resultados do DBpedia",
    label_frontal:          "frontal",
    grupo_general:          "Geral",
    grupo_procesador:       "Processador",
    grupo_memoria:          "Memória",
    grupo_bateria:          "Bateria",
    grupo_pantalla:         "Tela",
    grupo_camara_trasera:   "Câmera Traseira",
    grupo_camara_frontal:   "Câmera Frontal",
    grupo_so:               "Sistema Operacional",
    grupo_audio:            "Áudio",
    grupo_red_movil:        "Rede Móvel",
    grupo_conectividad:     "Conectividade sem Fio",
    grupo_sensores:         "Sensores",
    grupo_resistencia:      "Resistência",
    grupo_sim:              "Tipo de SIM",
    prop_marca:             "Marca",
    prop_modelo:            "Modelo",
    prop_gama:              "Categoria",
    prop_precio:            "Preço (USD)",
    prop_anio:              "Ano",
    prop_fabricante_cpu:    "Fabricante CPU",
    prop_modelo_cpu:        "Modelo CPU",
    prop_nucleos:           "Núcleos",
    prop_frecuencia_max:    "Freq. Máx. (GHz)",
    prop_ram:               "RAM (GB)",
    prop_almacenamiento:    "Armazenamento (GB)",
    prop_microsd:           "MicroSD",
    prop_capacidad:         "Capacidade (mAh)",
    prop_carga_rapida:      "Carga Rápida",
    prop_carga_inalambrica: "Carga sem Fio",
    prop_tipo_pantalla:     "Tipo",
    prop_tamano_pantalla:   "Tamanho (pol.)",
    prop_tasa_refresco:     "Taxa de Atualização (Hz)",
    prop_resolucion:        "Resolução",
    prop_resolucion_principal: "Resolução Principal (MP)",
    prop_num_camaras:       "Número de Câmeras",
    prop_resolucion_frontal:"Resolução Frontal (MP)",
    prop_so:                "Sistema Operacional",
    prop_salida_audio:      "Saída de Áudio",
    prop_red_movil:         "Rede Móvel",
    prop_tecnologia:        "Tecnologia",
    prop_sensor:            "Sensor",
    prop_certificacion_ip:  "Certificação IP",
    prop_descripcion:       "Descrição",
    bool_true:              "✓ Sim",
    bool_false:             "✗ Não",
    // Chaves faltantes
    prop_tipo_sim:          "Tipo",
    prop_label_red:         "Rótulo",
    prop_fuente_dbp:        "Fonte DBpedia",
    prop_enlace_dbp:        "Link DBpedia",
    prop_imagen_dbp:        "Imagem DBpedia",
  },
};

let currentLang = localStorage.getItem("lang") || "es";
function t(key, ...args) {
  const val = I18N[currentLang]?.[key] ?? I18N["es"][key] ?? key;
  return typeof val === "function" ? val(...args) : val;
}

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem("lang", lang);
  document.documentElement.lang = lang;

  // Nav links
  document.querySelector('.nav-link[data-view="buscador"]').textContent  = t("nav_buscador");
  document.querySelector('.nav-link[data-view="consultas"]').textContent = t("nav_consultas");
  const _dbpNavLink = document.querySelector('.nav-link[data-view="dbpedia"]');
  if (_dbpNavLink) _dbpNavLink.textContent = t("nav_dbpedia");
  document.querySelector('.nav-link[data-view="multilang"]').textContent = t("nav_multilang");

  // Stats labels
  const statLabels = document.querySelectorAll(".stat-label");
  const keys = ["stat_celulares","stat_clases","stat_tripletas","stat_consultas"];
  statLabels.forEach((el, i) => { if (keys[i]) el.textContent = t(keys[i]); });

  // Search inputs & buttons
  const si = document.getElementById("searchInput");
  if (si) si.placeholder = t("search_placeholder");
  const btnB = document.getElementById("btnBuscar");
  if (btnB) btnB.textContent = t("btn_buscar");
  const dbpSi = document.getElementById("dbpSearchInput");
  if (dbpSi) dbpSi.placeholder = t("dbp_search_placeholder");
  const dbpBtn = document.getElementById("dbpBtnBuscar");
  if (dbpBtn) dbpBtn.textContent = t("dbp_btn_buscar");

  // Sug labels
  document.querySelectorAll(".sug-label").forEach(el => el.textContent = t("sug_label"));

  // Re-renderizar chips de sugerencia del buscador principal
  const sugContainer = document.getElementById("sugBuscador");
  if (sugContainer) {
    const chips = I18N[lang].sug_chips || [];
    sugContainer.innerHTML =
      `<span class="sug-label">${t("sug_label")}</span>` +
      chips.map(chip =>
        `<button class="sug-chip" onclick="buscarTermino('${chip}')">${chip}</button>`
      ).join("");
  }

  // Re-renderizar chips de sugerencia de DBpedia (nombres de marcas, no cambian con idioma)
  // Los dejamos estáticos ya que son nombres propios

  // DBpedia connected badge
  const dot = document.querySelector(".dbp-badge");
  if (dot) dot.innerHTML = `<span class="dbp-dot"></span>${t("dbp_connected")}`;

  // Query search placeholder
  const qs = document.getElementById("querySearch");
  if (qs) qs.placeholder = t("query_search_ph");

  // Categories sidebar title
  const sideH3 = document.querySelector(".cat-sidebar h3");
  if (sideH3) sideH3.textContent = t("cats_sidebar");

  // Footer
  const footer = document.getElementById("mainFooter") || document.querySelector("footer");
  if (footer) footer.textContent = t("footer");

  // Empty init block
  const emptyInit = document.getElementById("emptyInit");
  if (emptyInit) {
    emptyInit.querySelector("h3").textContent = t("empty_init_h3");
    emptyInit.querySelector("p").textContent  = t("empty_init_p");
  }

  // DBpedia empty default
  const dbpGridDefault = document.querySelector("#dbpGrid .empty h3");
  const dbpGridDefaultP = document.querySelector("#dbpGrid .empty p");
  if (dbpGridDefault) dbpGridDefault.textContent = t("dbp_empty_h3");
  if (dbpGridDefaultP) dbpGridDefaultP.textContent = t("dbp_empty_p");

  // Modal title placeholder
  const modalTitleEl = document.getElementById("modalTitle");
  if (modalTitleEl && modalTitleEl.textContent === "Detalle del dispositivo" ||
      modalTitleEl && modalTitleEl.textContent === "Device detail" ||
      modalTitleEl && modalTitleEl.textContent === "Detalhe do dispositivo") {
    modalTitleEl.textContent = t("modal_detalle");
  }

  // Retitle header if currently showing
  const currentView = getHash();
  document.getElementById("headerTitle").innerHTML = t(`header_${currentView}_h1`);
  document.title = t(`page_${currentView}`);

  const sparqlBtn = document.getElementById("sparqlToggleBtn");
  if (sparqlBtn) sparqlBtn.textContent = t("btn_ver_sparql");

  // "Todas" / "All" button in consultas sidebar (if already loaded)
  const todasBtn = document.querySelector(".cat-btn:first-child span:first-child");
  if (todasBtn) todasBtn.textContent = t("cat_todas");

  // Re-render "agregar" buttons in DBpedia grid (not yet clicked)
  document.querySelectorAll(".btn-agregar-dbp:not(:disabled)").forEach(b => {
    if (!b.classList.contains("btn-agregado")) b.textContent = t("btn_agregar");
  });

  // Highlight active lang button
  document.querySelectorAll(".lang-btn").forEach(b => {
    b.classList.toggle("lang-active", b.dataset.lang === lang);
  });


  // ── Sección multilingüe ──
  const mlBadge = document.querySelector(".ml-badge");
  if (mlBadge) mlBadge.innerHTML = `<span class="ml-icon">🗣</span> ${t("ml_badge_texto")}`;

  const mlLangLabel = document.querySelector(".ml-lang-label");
  if (mlLangLabel) mlLangLabel.textContent = t("ml_lang_label");

  const mlLoader = document.querySelector("#mlLoader .dot-anim");
  if (mlLoader) mlLoader.textContent = t("ml_consultando");

  // Stats de la sección multilingüe (por ID para no confundir con .stat-label global)
  const mlStatClasesEl  = document.getElementById("mlStatClases");
  const mlStatObjEl     = document.getElementById("mlStatObj");
  const mlStatDatoEl    = document.getElementById("mlStatDato");
  const mlStatIndivEl   = document.getElementById("mlStatIndiv");
  if (mlStatClasesEl) mlStatClasesEl.textContent = t("ml_clases_stat");
  if (mlStatObjEl)    mlStatObjEl.textContent    = t("ml_props_obj_stat");
  if (mlStatDatoEl)   mlStatDatoEl.textContent   = t("ml_props_dato_stat");
  if (mlStatIndivEl)  mlStatIndivEl.textContent   = t("ml_indiv_stat");

  // Títulos de sección
  const mlTitleClasesEl = document.getElementById("mlTitleClases");
  const mlTitleObjEl    = document.getElementById("mlTitlePropsObj");
  const mlTitleDatoEl   = document.getElementById("mlTitlePropsDato");
  const mlTitleIndivEl  = document.getElementById("mlTitleIndividuos");
  if (mlTitleClasesEl) mlTitleClasesEl.textContent = t("ml_titulo_clases");
  if (mlTitleObjEl)    mlTitleObjEl.textContent    = t("ml_titulo_obj");
  if (mlTitleDatoEl)   mlTitleDatoEl.textContent   = t("ml_titulo_dato");
  if (mlTitleIndivEl)  mlTitleIndivEl.textContent   = t("ml_titulo_indiv");

  // Botones "Ver SPARQL" de la sección multilingüe
  document.querySelectorAll("#view-multilang .sparql-toggle button").forEach(btn => {
    btn.textContent = t("ml_ver_sparql");
  });

  // Si la sección multilingüe ya estaba cargada, recargarla con el nuevo idioma
  if (typeof mlCargada !== "undefined" && mlCargada && typeof mlCargar === "function") {
    mlCargar(lang);
  }

  // Fix 3: NO relanzar la búsqueda al cambiar idioma.
  // Solo se actualiza la interfaz. El usuario puede presionar Buscar
  // si quiere re-buscar en el nuevo idioma. Esto evita resultados
  // incorrectos por NLP y evita recargar DBpedia innecesariamente.

  // Re-renderizar las tarjetas ya cargadas con el nuevo idioma (labels de gama, fuente, etc.)
  if (typeof _lastLocalResultados !== "undefined" && (_lastLocalResultados.length > 0 || _lastDbpResultados.length > 0)) {
    renderCardsMixed(_lastLocalResultados, _lastDbpResultados);
    if (_lastLocalResultados.length > 0 && _lastDbpResultados.length > 0) {
      resultsCount.textContent = t("results_count_combined", _lastLocalResultados.length, _lastDbpResultados.length);
    } else if (_lastLocalResultados.length > 0) {
      resultsCount.textContent = t("results_count", _lastLocalResultados.length);
    }
  }

}

// ═══════════════════════════════════════════════════════════════════
// 1. HASH ROUTER
// ═══════════════════════════════════════════════════════════════════

const VIEWS = {
  buscador:  document.getElementById("view-buscador"),
  consultas: document.getElementById("view-consultas"),
  multilang: document.getElementById("view-multilang"),
};

// TITLES now resolves dynamically via i18n
function getTitles(view) {
  return { h1: t(`header_${view}_h1`), page: t(`page_${view}`) };
}

function getHash() {
  const h = window.location.hash.replace("#", "").trim();
  return VIEWS[h] ? h : "buscador";
}

function navigateTo(view, pushState = true) {
  const target = VIEWS[view] ? view : "buscador";

  Object.values(VIEWS).forEach(v => {
    v.style.display = "none";
    v.classList.remove("view-enter");
  });

  VIEWS[target].style.display = "block";
  requestAnimationFrame(() => VIEWS[target].classList.add("view-enter"));

  document.querySelectorAll(".nav-link").forEach(a => {
    a.classList.toggle("active", a.dataset.view === target);
  });

  document.getElementById("headerTitle").innerHTML = getTitles(target).h1;
  document.title = getTitles(target).page;

  if (pushState) {
    history.pushState({ view: target }, "", `#${target}`);
  }

  if (target === "consultas" && !consultasCargadas) {
    cargarConsultas();
  }
  if (target === "multilang" && !mlCargada) {
    // mlCargada se define en sección 6; usar timeout para que exista
    setTimeout(() => { if (typeof mlCargar === "function") mlCargar(mlLangActual || currentLang); }, 0);
  }
}

document.querySelectorAll(".nav-link[data-view]").forEach(a => {
  a.addEventListener("click", e => {
    e.preventDefault();
    navigateTo(a.dataset.view);
  });
});

window.addEventListener("popstate", () => {
  navigateTo(getHash(), false);
});


// ═══════════════════════════════════════════════════════════════════
// 2. BUSCADOR LOCAL
// ═══════════════════════════════════════════════════════════════════

const grid         = document.getElementById("grid");
const searchInput  = document.getElementById("searchInput");
const resultsCount = document.getElementById("resultsCount");
const semBadges    = document.getElementById("semanticBadges");
const btnBuscar    = document.getElementById("btnBuscar");
const modalBg      = document.getElementById("modalBg");
const modalClose   = document.getElementById("modalClose");
const modalTitle   = document.getElementById("modalTitle");
const modalContent = document.getElementById("modalContent");

searchInput.addEventListener("keydown", e => {
  if (e.key === "Enter") buscar();
});
btnBuscar.addEventListener("click", buscar);

function buscarTermino(termino) {
  searchInput.value = termino;
  buscar();
}

// Cache de la última búsqueda para re-renderizar al cambiar idioma
let _lastLocalResultados = [];
let _lastDbpResultados   = [];

// AbortController para cancelar búsquedas anteriores (evita race condition)
let _buscarAbortController = null;

// Token de versión: cada búsqueda incrementa el contador.
// Si al resolver un fetch el token ya cambió, los resultados se descartan.
let _buscarToken = 0;

// ── Helpers de renderizado ──────────────────────────────────────────

function tagGama(gama) {
  const g = (gama || "").toLowerCase();
  if (g === "alta")  return `<span class="tag tag-gama-alta">${t("gama_alta")}</span>`;
  if (g === "media") return `<span class="tag tag-gama-media">${t("gama_media")}</span>`;
  if (g === "baja")  return `<span class="tag tag-gama-baja">${t("gama_baja")}</span>`;
  return gama !== "—" ? `<span class="tag tag-gama-def">${gama}</span>` : "";
}

function tagDBpedia() {
  return `<span class="tag tag-dbpedia" title="Importado desde DBpedia">🌐 DBpedia</span>`;
}

function mostrarBadgesSemánticos(filtros, sugerencias) {
  const items = [];
  if (filtros) {
    if (filtros.gama)     items.push(`🏷 Gama: ${filtros.gama}`);
    if (filtros.so)       items.push(`📱 SO: ${filtros.so}`);
    if (filtros.ram)      items.push(`💾 RAM: ${filtros.ram} GB`);
    if (filtros.marca)    items.push(`🏭 Marca: ${filtros.marca}`);
    if (filtros.cpu)      items.push(`⚙️ CPU: ${filtros.cpu}`);
    if (filtros.pantalla) items.push(`🖥 Pantalla: ${filtros.pantalla}`);
    if (filtros.red)      items.push(`📶 Red: ${filtros.red}`);
  }
  const fuzzyHtml = (sugerencias || []).map(s =>
    `<span class="sem-badge sem-badge-fuzzy" title="Interpretado automáticamente">
      ✏️ "${s.original}" → ${s.interpretado}
    </span>`
  ).join("");

  if (items.length === 0 && !fuzzyHtml) { semBadges.style.display = "none"; return; }

  semBadges.style.display = "flex";
  semBadges.innerHTML =
    `<span class="sem-label">${t("detected")}</span>` +
    items.map(i => `<span class="sem-badge">${i}</span>`).join("") +
    fuzzyHtml;
}

function renderCards(resultados) {
  grid.innerHTML = "";
  if (resultados.length === 0) {
    grid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">📭</div>
        <h3>${t("empty_h3")}</h3>
        <p>${t("empty_p")}</p>
      </div>`;
    return;
  }
  resultados.forEach((c, i) => {
    const div = document.createElement("div");
    div.className = "card";
    div.style.animationDelay = `${i * 0.035}s`;

    const precio = c.precio !== "—"
      ? `<div class="card-precio">$ ${parseFloat(c.precio).toLocaleString()}</div>` : "";
    const ramTag  = c.ram  !== "—" ? `<span class="tag tag-ram">${c.ram} GB RAM</span>` : "";
    const almTag  = c.almacenamiento !== "—" ? `<span class="tag tag-ram">${c.almacenamiento} GB</span>` : "";
    const soTag   = c.so   !== "—" ? `<span class="tag tag-so">${c.so}</span>` : "";
    const anioTag = c.anio !== "—" ? `<span class="tag tag-anio">${c.anio}</span>` : "";
    const redTag  = c.redMovil !== "—" ? `<span class="tag tag-anio">${c.redMovil}</span>` : "";
    const certTag = c.certificacion !== "—" ? `<span class="tag tag-gama-def">${c.certificacion}</span>` : "";

    // Etiqueta DBpedia si el celular fue importado
    const dbpTag  = c.fuenteDBpedia ? tagDBpedia() : "";

    const specs = [];
    if (c.tipoPantalla !== "—" || c.tamanoPantalla !== "—") {
      const tam = c.tamanoPantalla !== "—" ? `${c.tamanoPantalla}"` : "";
      const tip = c.tipoPantalla   !== "—" ? c.tipoPantalla : "";
      const ref = c.tasaRefresco   !== "—" ? ` · ${c.tasaRefresco}Hz` : "";
      specs.push(`🖥 ${[tam, tip].filter(Boolean).join(" ")}${ref}`);
    }
    if (c.bateria !== "—") {
      let bat = `🔋 ${c.bateria} mAh`;
      if (c.cargaRapida === "true" || c.cargaRapida === "✓ Sí") bat += " ⚡";
      if (c.cargaInalambrica === "true" || c.cargaInalambrica === "✓ Sí") bat += " 🔌";
      specs.push(bat);
    }
    if (c.camTrasera !== "—") specs.push(`📷 ${c.camTrasera} MP`);
    if (c.camFrontal !== "—") specs.push(`⚙ ${c.camFrontal} MP ${t("label_frontal")}`);

    const specsHtml = specs.length
      ? `<div class="card-specs">${specs.map(s => `<span>${s}</span>`).join("")}</div>`
      : "";

    div.innerHTML = `
      ${dbpTag ? `<div class="card-dbpedia-corner">${dbpTag}</div>` : ""}
      <div class="card-brand">${c.marca}</div>
      <div class="card-model">${c.modelo}</div>
      <div class="card-tags">${tagGama(c.gama)}${soTag}${ramTag}${almTag}${redTag}${certTag}${anioTag}</div>
      ${specsHtml}
      ${precio}`;
    div.addEventListener("click", () => abrirDetalle(c.uri, `${c.marca} ${c.modelo}`));
    grid.appendChild(div);
  });
}

async function buscar() {
  const q = searchInput.value.trim();

  // Fix 1: Si no hay término, mostrar estado inicial y salir
  if (!q) {
    grid.innerHTML = `
      <div class="empty" id="emptyInit">
        <div class="empty-icon">🔍</div>
        <h3>${t("empty_init_h3")}</h3>
        <p>${t("empty_init_p")}</p>
      </div>`;
    semBadges.style.display = "none";
    resultsCount.textContent = "";
    return;
  }

  // Cancelar la búsqueda anterior si todavía estaba en vuelo
  if (_buscarAbortController) {
    _buscarAbortController.abort();
  }
  // Limpiar loader de DBpedia de búsqueda anterior si quedó colgado
  const loaderViejo = document.getElementById("dbp-inline-loader");
  if (loaderViejo) loaderViejo.remove();

  _buscarAbortController = new AbortController();
  const signal = _buscarAbortController.signal;

  // Token de esta búsqueda — si cambia antes de que llegue la respuesta, la descartamos
  const token = ++_buscarToken;

  grid.innerHTML = `
    <div class="loader-inline">
      <span class="dot-anim">${t("loading_ontologia")}</span>
    </div>`;
  semBadges.style.display = "none";
  resultsCount.textContent = "";

  // ── 1. Resultados LOCALES primero (rápidos) ────────────────────
  let localResultados = [];
  try {
    const res  = await fetch(`/buscar?q=${encodeURIComponent(q)}&filtro=todos&lang=${currentLang}`, { signal });
    if (token !== _buscarToken) return;
    const data = await res.json();

    // Si ya hubo una búsqueda más nueva, descartar esta respuesta
    if (token !== _buscarToken) return;

    localResultados = data.resultados || [];
    _lastLocalResultados = localResultados;
    _lastDbpResultados   = [];
    resultsCount.textContent = t("results_count", localResultados.length);
    semBadges.style.display = "none";

    renderCardsMixed(localResultados, []);

    if (!q) return;
  } catch (e) {
    if (e.name === "AbortError") return; // búsqueda cancelada, ignorar silenciosamente
    grid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">⚠️</div>
        <h3>${t("error_conexion_h3")}</h3>
        <p>${t("error_conexion_p")}</p>
      </div>`;
    return;
  }

  // ── 2. DBpedia en PARALELO (puede tardar, no bloquea UI) ────────
  const dbpLoader = document.createElement("div");
  dbpLoader.id = "dbp-inline-loader";
  dbpLoader.className = "dbp-inline-loader";
  dbpLoader.innerHTML = `<span class="dot-anim dbp-dot-anim">🌐 ${t("loading_dbpedia")}</span>`;
  grid.appendChild(dbpLoader);

  try {
    const dbpLang = currentLang === "es" ? "es" : currentLang === "pt" ? "pt" : "en";
    const dbpRes  = await fetch(`/api/dbpedia/buscar?q=${encodeURIComponent(q)}&lang=${dbpLang}`, { signal });
    if (token !== _buscarToken) { const l = document.getElementById("dbp-inline-loader"); if (l) l.remove(); return; }
    const dbpData = await dbpRes.json();

    // Si ya hubo una búsqueda más nueva, descartar esta respuesta
    if (token !== _buscarToken) { const l = document.getElementById("dbp-inline-loader"); if (l) l.remove(); return; }

    const dbpResultados = dbpData.resultados || [];
    _lastDbpResultados = dbpResultados;

    const loaderEl = document.getElementById("dbp-inline-loader");
    if (loaderEl) loaderEl.remove();

    resultsCount.textContent = t("results_count_combined", localResultados.length, dbpResultados.length);
    renderCardsMixed(localResultados, dbpResultados);
  } catch (e) {
    const loaderEl = document.getElementById("dbp-inline-loader");
    if (loaderEl) loaderEl.remove();
    if (e.name === "AbortError") return; // cancelada, no hacer nada
    // DBpedia falló, los locales ya están visibles
  }
}

// Renderiza locales + DBpedia en un solo grid, locales primero con sus etiquetas
function renderCardsMixed(locales, dbpResultados) {
  grid.innerHTML = "";
  const total = locales.length + dbpResultados.length;

  if (total === 0) {
    grid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">📭</div>
        <h3>${t("empty_h3")}</h3>
        <p>${t("empty_p")}</p>
      </div>`;
    return;
  }

  // Tarjetas locales con etiqueta fuente
  locales.forEach((c, i) => {
    const div = document.createElement("div");
    div.className = "card card-local";
    div.style.animationDelay = `${i * 0.035}s`;

    const precio = c.precio !== "—"
      ? `<div class="card-precio">$ ${parseFloat(c.precio).toLocaleString()}</div>` : "";
    const ramTag  = c.ram  !== "—" ? `<span class="tag tag-ram">${c.ram} GB RAM</span>` : "";
    const almTag  = c.almacenamiento !== "—" ? `<span class="tag tag-ram">${c.almacenamiento} GB</span>` : "";
    const soTag   = c.so   !== "—" ? `<span class="tag tag-so">${c.so}</span>` : "";
    const anioTag = c.anio !== "—" ? `<span class="tag tag-anio">${c.anio}</span>` : "";
    const redTag  = c.redMovil !== "—" ? `<span class="tag tag-anio">${c.redMovil}</span>` : "";
    const certTag = c.certificacion !== "—" ? `<span class="tag tag-gama-def">${c.certificacion}</span>` : "";
    const dbpImportTag = c.fuenteDBpedia ? tagDBpedia() : "";
    const localTag = !c.fuenteDBpedia
      ? `<span class="tag tag-local" title="${t("tag_local_tooltip")}">🏠 ${t("tag_local")}</span>`
      : "";

    const specs = [];
    if (c.tipoPantalla !== "—" || c.tamanoPantalla !== "—") {
      const tam = c.tamanoPantalla !== "—" ? `${c.tamanoPantalla}"` : "";
      const tip = c.tipoPantalla   !== "—" ? c.tipoPantalla : "";
      const ref = c.tasaRefresco   !== "—" ? ` · ${c.tasaRefresco}Hz` : "";
      specs.push(`🖥 ${[tam, tip].filter(Boolean).join(" ")}${ref}`);
    }
    if (c.bateria !== "—") {
      let bat = `🔋 ${c.bateria} mAh`;
      if (c.cargaRapida === "true" || c.cargaRapida === "✓ Sí") bat += " ⚡";
      if (c.cargaInalambrica === "true" || c.cargaInalambrica === "✓ Sí") bat += " 🔌";
      specs.push(bat);
    }
    if (c.camTrasera !== "—") specs.push(`📷 ${c.camTrasera} MP`);
    if (c.camFrontal !== "—") specs.push(`⚙ ${c.camFrontal} MP ${t("label_frontal")}`);

    const specsHtml = specs.length
      ? `<div class="card-specs">${specs.map(s => `<span>${s}</span>`).join("")}</div>`
      : "";

    div.innerHTML = `
      <div class="card-source-badge">${localTag}${dbpImportTag}</div>
      <div class="card-brand">${c.marca}</div>
      <div class="card-model">${c.modelo}</div>
      <div class="card-tags">${tagGama(c.gama)}${soTag}${ramTag}${almTag}${redTag}${certTag}${anioTag}</div>
      ${specsHtml}
      ${precio}`;
    div.addEventListener("click", () => abrirDetalle(c.uri, `${c.marca} ${c.modelo}`));
    grid.appendChild(div);
  });

  // Separador y tarjetas DBpedia completas (iguales a la pestaña DBpedia)
  if (dbpResultados.length > 0) {
    const sep = document.createElement("div");
    sep.className = "grid-section-sep";
    sep.innerHTML = `<span>🌐 ${t("dbp_section_label")} (${dbpResultados.length})</span>`;
    grid.appendChild(sep);

    dbpResultados.forEach((c, i) => {
      const div = document.createElement("div");
      div.className = "card card-dbp";
      div.style.animationDelay = `${(locales.length + i) * 0.04}s`;

      const nombreDisplay = c.nombre || c.nombre_recurso.replace(/_/g, " ");
      const imgHtml = c.imagen
        ? `<div class="dbp-card-img"><img src="${c.imagen}" alt="${nombreDisplay}" onerror="this.parentElement.style.display='none'"></div>`
        : "";
      const descHtml = c.descripcion
        ? `<p class="dbp-card-desc">${c.descripcion.substring(0, 180)}${c.descripcion.length > 180 ? "…" : ""}</p>`
        : "";
      const dbpLink = c.enlace_dbpedia
        ? `<a href="${c.enlace_dbpedia}" target="_blank" class="dbp-link">🔗 DBpedia</a>`
        : "";

      div.innerHTML = `
        <div class="dbp-card-top">
          <span class="tag tag-dbpedia">🌐 DBpedia</span>
          <span class="dbp-card-recurso">${c.nombre_recurso.replace(/_/g, " ")}</span>
        </div>
        ${imgHtml}
        <div class="card-model" style="margin-top:0.5rem">${nombreDisplay}</div>
        ${descHtml}
        <div class="dbp-card-links">${dbpLink}</div>
        <button class="btn-agregar-dbp" data-idx="${i}">${t("btn_agregar")}</button>
      `;

      const btn = div.querySelector(".btn-agregar-dbp");
      btn.addEventListener("click", e => {
        e.stopPropagation();
        dbpAgregarOntologia(c, btn);
      });

      grid.appendChild(div);
    });
  }
}

// ── Detalle celular ───────────────────────────────────────────────

async function abrirDetalle(uri, titulo) {
  modalTitle.textContent = titulo;
  modalBg.classList.add("open");
  document.body.style.overflow = "hidden";

  modalContent.innerHTML = `
    <div style="color:var(--muted);font-size:0.83rem;padding:1rem 0;font-family:'Space Mono',monospace">
      <span class="dot-anim">${t("loading_specs")}</span>
    </div>`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const res  = await fetch(`/detalle/${encodeURIComponent(uri)}?lang=${currentLang}`, { signal: controller.signal });
    clearTimeout(timeout);
    const data = await res.json();

    // El backend ya devuelve grupos y propiedades con labels en el idioma correcto.
    // __grupos_orden__ trae la secuencia preferida de secciones.
    const ordenados = (data["__grupos_orden__"] || Object.keys(data))
      .filter(g => g !== "__grupos_orden__" && data[g] && typeof data[g] === "object");

    const gruposHtml = ordenados.map(grupo => {
      const props = data[grupo];
      const filas = Object.entries(props)
        .filter(([k]) => k !== "type")
        .map(([k, v]) => `
          <div class="prop-row">
            <span class="prop-key">${k}</span>
            <span class="prop-val">${v === "__bool_true__" ? t("bool_true") : v === "__bool_false__" ? t("bool_false") : v}</span>
          </div>`).join("");
      return filas ? `
        <div class="detalle-grupo">
          <div class="detalle-grupo-titulo">${grupo}</div>
          ${filas}
        </div>` : "";
    }).join("");

    modalContent.innerHTML = gruposHtml;

  } catch (e) {
    const msg = e.name === "AbortError"
      ? t("timeout_error")
      : `⚠️ ${e.message}`;
    modalContent.innerHTML = `<p style='color:var(--muted);font-family:"Space Mono",monospace;font-size:0.82rem;padding:1rem 0'>${msg}</p>`;
  }
}

modalClose.addEventListener("click", () => { modalBg.classList.remove("open"); document.body.style.overflow = ""; });
modalBg.addEventListener("click", e => { if (e.target === modalBg) { modalBg.classList.remove("open"); document.body.style.overflow = ""; } });


// ═══════════════════════════════════════════════════════════════════
// 3. CONSULTAS SPARQL
// ═══════════════════════════════════════════════════════════════════

let consultasCargadas  = false;
let todasLasConsultas  = [];
let categoriaActiva    = null;
let currentSparql      = "";

async function cargarConsultas() {
  try {
    const res  = await fetch("/api/consultas");
    const data = await res.json();

    todasLasConsultas = [];
    for (const cat of data.categorias) {
      for (const q of (data.consultas[cat] || [])) {
        todasLasConsultas.push(q);
      }
    }

    const catList = document.getElementById("catList");
    catList.innerHTML = "";

    const btnTodas = document.createElement("button");
    btnTodas.className = "cat-btn active";
    btnTodas.innerHTML = `<span>${t("cat_todas")}</span><span class="cat-badge">${todasLasConsultas.length}</span>`;
    btnTodas.addEventListener("click", () => seleccionarCategoria(null, btnTodas));
    catList.appendChild(btnTodas);

    for (const cat of data.categorias) {
      const count = (data.consultas[cat] || []).length;
      const btn   = document.createElement("button");
      btn.className = "cat-btn";
      btn.innerHTML = `<span>${cat}</span><span class="cat-badge">${count}</span>`;
      btn.addEventListener("click", () => seleccionarCategoria(cat, btn));
      catList.appendChild(btn);
    }

    consultasCargadas = true;
    renderQueryList(todasLasConsultas);
  } catch (e) {
    document.getElementById("queryList").innerHTML =
      `<div class="no-results-q">⚠️ Error cargando consultas. Verificá Flask.</div>`;
  }
}

function seleccionarCategoria(cat, btnEl) {
  categoriaActiva = cat;
  document.querySelectorAll(".cat-btn").forEach(b => b.classList.remove("active"));
  btnEl.classList.add("active");
  const filtradas = cat
    ? todasLasConsultas.filter(q => q.categoria === cat)
    : todasLasConsultas;
  renderQueryList(filtradas);
  document.getElementById("querySearch").value = "";
}

function renderQueryList(lista) {
  const container = document.getElementById("queryList");
  if (lista.length === 0) {
    container.innerHTML = `<div class="no-results-q">Sin resultados para este filtro</div>`;
    return;
  }
  container.innerHTML = lista.map(q => `
    <div class="query-card" onclick="ejecutarConsulta(${q.id})">
      <span class="query-num">#${String(q.id).padStart(2, "0")}</span>
      <div class="query-body">
        <div class="query-title">${q.titulo}</div>
        <div class="query-desc">${q.descripcion}</div>
      </div>
      <span class="query-badge ${q.tipo === "ASK" ? "badge-ask" : "badge-select"}">${q.tipo}</span>
    </div>`).join("");
}

document.getElementById("querySearch").addEventListener("input", function () {
  const term = this.value.toLowerCase().trim();
  const base = categoriaActiva
    ? todasLasConsultas.filter(q => q.categoria === categoriaActiva)
    : todasLasConsultas;
  renderQueryList(term
    ? base.filter(q =>
        q.titulo.toLowerCase().includes(term) ||
        q.descripcion.toLowerCase().includes(term))
    : base);
});

async function ejecutarConsulta(id) {
  const panel      = document.getElementById("resultPanel");
  const rpTitle    = document.getElementById("rpTitle");
  const rpDesc     = document.getElementById("rpDesc");
  const rpBody     = document.getElementById("rpBody");
  const sparqlCode = document.getElementById("sparqlCode");

  panel.classList.add("visible");
  if (!document.getElementById("resultPanelClose")) {
    const closeBtn = document.createElement("button");
    closeBtn.id = "resultPanelClose";
    closeBtn.className = "rp-close-btn";
    closeBtn.textContent = t("btn_cerrar");
    closeBtn.addEventListener("click", () => {
      panel.classList.remove("visible");
    });
    panel.appendChild(closeBtn);
  }
  rpTitle.textContent = t("executing");
  rpDesc.textContent  = "";
  rpBody.innerHTML    = `<div style="padding:1.5rem;text-align:center;color:var(--muted);font-family:'Space Mono',monospace;font-size:0.8rem;"><span class="dot-anim">Consultando ontología</span></div>`;
  sparqlCode.classList.remove("open");
  panel.scrollIntoView({ behavior: "smooth", block: "start" });

  try {
    const res  = await fetch(`/api/consulta/${id}`);
    const data = await res.json();

    rpTitle.textContent = `#${String(data.id).padStart(2, "00")} — ${data.titulo}`;
    rpDesc.textContent  = data.descripcion;
    currentSparql       = data.sparql || "";
    sparqlCode.textContent = currentSparql;

    if (data.error) {
      rpBody.innerHTML = `<div style="padding:1.5rem;color:var(--danger);font-family:'Space Mono',monospace;font-size:0.8rem;">⚠ Error: ${data.error}</div>`;
      return;
    }

    if (data.tipo === "ASK") {
      const si = data.respuesta;
      rpBody.innerHTML = `
        <div class="ask-result">
          <div class="ask-icon">${si ? "✅" : "❌"}</div>
          <div class="ask-text ${si ? "ask-yes" : "ask-no"}">${data.texto}</div>
        </div>`;
    } else {
      const { columnas, filas, total } = data;
      const metaHtml = `<div class="rp-meta"><span class="rp-count">${t("rows_returned", total)}</span></div>`;
      if (total === 0) {
        rpBody.innerHTML = metaHtml + `<div class="no-results-q">${t("no_results_query")}</div>`;
        return;
      }
      const thead = columnas.map(c => `<th>${c}</th>`).join("");
      const tbody = filas.map(f =>
        "<tr>" + columnas.map(c => `<td title="${f[c] || "—"}">${f[c] || "—"}</td>`).join("") + "</tr>"
      ).join("");
      rpBody.innerHTML = metaHtml + `
        <div class="result-table-wrap">
          <table class="result-table">
            <thead><tr>${thead}</tr></thead>
            <tbody>${tbody}</tbody>
          </table>
        </div>`;
    }
  } catch (e) {
    rpBody.innerHTML = `<div style="padding:1.5rem;color:var(--danger);font-size:0.85rem;">⚠ Error de conexión con Flask.</div>`;
  }
}

function toggleSparql() {
  const code = document.getElementById("sparqlCode");
  code.classList.toggle("open");
  const btn = document.querySelector(".sparql-toggle button");
  if (btn) btn.textContent = t("btn_ver_sparql");
}


// ═══════════════════════════════════════════════════════════════════
// 4. DBPEDIA ONLINE
// ═══════════════════════════════════════════════════════════════════

const dbpGrid         = document.getElementById("dbpGrid");
const dbpSearchInput  = document.getElementById("dbpSearchInput");
const dbpResultsCount = document.getElementById("dbpResultsCount");
const dbpBtnBuscar    = document.getElementById("dbpBtnBuscar");
const dbpNotif        = document.getElementById("dbpNotif");

dbpSearchInput.addEventListener("keydown", e => {
  if (e.key === "Enter") dbpBuscar();
});
dbpBtnBuscar.addEventListener("click", dbpBuscar);

function dbpBuscarTermino(termino) {
  dbpSearchInput.value = termino;
  dbpBuscar();
}

function dbpMostrarNotif(msg, tipo = "ok", anchorEl = null) {
  // Si hay un elemento ancla (botón en el buscador), mostrar toast flotante
  if (anchorEl) {
    const toast = document.createElement("div");
    toast.className = `dbp-toast dbp-toast-${tipo}`;
    toast.textContent = msg;
    document.body.appendChild(toast);
    const r = anchorEl.getBoundingClientRect();
    toast.style.top  = `${r.top + window.scrollY - 40}px`;
    toast.style.left = `${r.left}px`;
    setTimeout(() => toast.remove(), 3500);
    return;
  }
  // Vista DBpedia: notif normal
  dbpNotif.textContent = msg;
  dbpNotif.className   = `dbp-notif dbp-notif-${tipo}`;
  dbpNotif.style.display = "block";
  setTimeout(() => { dbpNotif.style.display = "none"; }, 4000);
}

async function dbpAgregarOntologia(celular, btnEl) {
  btnEl.disabled    = true;
  btnEl.textContent = t("btn_consultando");

  // La card contenedora del botón (funciona tanto en #grid como en #dbpGrid)
  const cardEl  = btnEl.closest(".card");
  const enGrid  = cardEl && cardEl.closest("#grid") !== null;

  try {
    const res  = await fetch("/api/dbpedia/agregar", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(celular),
    });
    const data = await res.json();

    if (data.ok) {
      btnEl.textContent = data.ya_existia ? t("btn_ya_existe") : t("btn_agregado");
      btnEl.classList.add("btn-agregado");

      if (!data.ya_existia && enGrid && cardEl) {
        // ── Insertar card local antes del separador DBpedia ──────────────────
        const nuevaCard = _buildLocalCard(data, celular);

        // Insertar antes del separador "Resultados de DBpedia"
        const sep = grid.querySelector(".grid-section-sep");
        nuevaCard.style.opacity    = "0";
        nuevaCard.style.transform  = "translateY(10px)";
        nuevaCard.style.transition = "opacity 0.3s, transform 0.3s";

        if (sep) {
          grid.insertBefore(nuevaCard, sep);
        } else {
          grid.appendChild(nuevaCard);
        }

        requestAnimationFrame(() => requestAnimationFrame(() => {
          nuevaCard.style.opacity   = "1";
          nuevaCard.style.transform = "translateY(0)";
        }));

      } else if (!data.ya_existia) {
        // Vista DBpedia dedicada — solo mostrar notificación
        dbpMostrarNotif(data.mensaje || t("btn_agregado"), "ok");
      }

    } else {
      btnEl.disabled    = false;
      btnEl.textContent = t("btn_agregar");
      const anchor = enGrid ? btnEl : null;
      dbpMostrarNotif("Error: " + (data.error || t("error_desconocido").replace("Error: ","")), "error", anchor);
    }
  } catch (e) {
    btnEl.disabled    = false;
    btnEl.textContent = t("btn_agregar");
    dbpMostrarNotif(t("error_flask"), "error", enGrid ? btnEl : null);
  }
}

// Construye la card local a partir de la respuesta del backend (campos ya saneados)
function _buildLocalCard(data, celular) {
  // Normaliza: null / undefined / "--" → vacío, el resto queda como string
  const v = x => (!x || x === "--") ? "" : String(x);

  const marca   = v(data.marca)  || celular.nombre_recurso.split("_")[0] || "";
  const modelo  = v(data.modelo) || v(celular.nombre) || celular.nombre_recurso.replace(/_/g, " ");
  const anio    = v(data.anio);
  const gama    = v(data.gama).toLowerCase();
  const so      = v(data.so);
  const ram     = v(data.ram_gb);
  const alm     = v(data.storage_gb);
  const bateria = v(data.bateria_mah);
  const red     = v(data.red_movil);
  const pantTipo = v(data.pantalla_tipo);
  const pantPulg = v(data.pantalla_pulgadas);
  const pantHz   = v(data.pantalla_hz);
  const camMP    = v(data.camara_trasera_mp);

  const soTag   = so    ? `<span class="tag tag-so">${so}</span>`           : "";
  const ramTag  = ram   ? `<span class="tag tag-ram">${ram} GB RAM</span>`  : "";
  const almTag  = alm   ? `<span class="tag tag-ram">${alm} GB</span>`      : "";
  const redTag  = red   ? `<span class="tag tag-anio">${red}</span>`        : "";
  const anioTag = anio  ? `<span class="tag tag-anio">${anio}</span>`       : "";

  const specs = [];
  if (pantTipo) {
    const pulgStr = pantPulg ? `${pantPulg}"` : "";
    const hzStr   = pantHz   ? ` · ${pantHz}Hz` : "";
    specs.push(`🖥 ${[pulgStr, pantTipo].filter(Boolean).join(" ")}${hzStr}`);
  }
  if (bateria) specs.push(`🔋 ${bateria} mAh`);
  if (camMP)   specs.push(`📷 ${camMP} MP`);

  const specsHtml = specs.length
    ? `<div class="card-specs">${specs.map(s => `<span>${s}</span>`).join("")}</div>`
    : "";

  const dbpTag = `<span class="tag tag-dbpedia" title="Importado desde DBpedia">🌐 DBpedia</span>`;

  const div = document.createElement("div");
  div.className = "card card-local";
  div.innerHTML = `
    <div class="card-source-badge">${dbpTag}</div>
    <div class="card-brand">${marca}</div>
    <div class="card-model">${modelo}</div>
    <div class="card-tags">${tagGama(gama)}${soTag}${ramTag}${almTag}${redTag}${anioTag}</div>
    ${specsHtml}`;

  if (data.uri) {
    div.style.cursor = "pointer";
    div.addEventListener("click", () => abrirDetalle(data.uri, `${marca} ${modelo}`));
  }

  return div;
}

function renderDbpCards(resultados) {
  dbpGrid.innerHTML = "";
  if (resultados.length === 0) {
    dbpGrid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">🌐</div>
        <h3>${t("dbp_sin_resultados_h3")}</h3>
        <p>${t("dbp_sin_resultados_p")}</p>
      </div>`;
    return;
  }

  resultados.forEach((c, i) => {
    const div = document.createElement("div");
    div.className = "card card-dbp";
    div.style.animationDelay = `${i * 0.04}s`;

    const nombreDisplay = c.nombre || c.nombre_recurso.replace(/_/g, " ");
    const imgHtml = c.imagen
      ? `<div class="dbp-card-img"><img src="${c.imagen}" alt="${nombreDisplay}" onerror="this.parentElement.style.display='none'"></div>`
      : "";
    const descHtml = c.descripcion
      ? `<p class="dbp-card-desc">${c.descripcion.substring(0, 180)}${c.descripcion.length > 180 ? "…" : ""}</p>`
      : "";
    const wikiLink = "";
    const dbpLink = c.enlace_dbpedia
      ? `<a href="${c.enlace_dbpedia}" target="_blank" class="dbp-link">🔗 DBpedia</a>`
      : "";

    div.innerHTML = `
      <div class="dbp-card-top">
        <span class="tag tag-dbpedia">🌐 DBpedia</span>
        <span class="dbp-card-recurso">${c.nombre_recurso.replace(/_/g, " ")}</span>
      </div>
      ${imgHtml}
      <div class="card-model" style="margin-top:0.5rem">${nombreDisplay}</div>
      ${descHtml}
      <div class="dbp-card-links">${wikiLink}${dbpLink}</div>
      <button class="btn-agregar-dbp" data-idx="${i}">${t("btn_agregar")}</button>
    `;

    const btn = div.querySelector(".btn-agregar-dbp");
    btn.addEventListener("click", e => {
      e.stopPropagation();
      dbpAgregarOntologia(c, btn);
    });

    dbpGrid.appendChild(div);
  });
}

async function dbpBuscar() {
  const q = dbpSearchInput.value.trim();
  if (!q) return;

  dbpGrid.innerHTML = `
    <div class="loader-inline">
      <span class="dot-anim">${t("loading_dbpedia")}</span>
    </div>`;
  dbpResultsCount.textContent = "";
  dbpNotif.style.display = "none";

  try {
    const res  = await fetch(`/api/dbpedia/buscar?q=${encodeURIComponent(q)}`);
    const data = await res.json();

    if (data.error && data.total === 0) {
      dbpGrid.innerHTML = `
        <div class="empty">
          <div class="empty-icon">⚠️</div>
          <h3>${t("error_dbpedia_h3")}</h3>
          <p>${data.error}</p>
        </div>`;
      return;
    }

    dbpResultsCount.textContent = t("dbp_results_count", data.total);
    renderDbpCards(data.resultados);
  } catch (e) {
    dbpGrid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">⚠️</div>
        <h3>${t("error_conexion_h3")}</h3>
        <p>${t("error_conexion_p")}</p>
      </div>`;
  }
}


// ═══════════════════════════════════════════════════════════════════
// 6. VISTA MULTILINGÜE — rdfs:label con @lang
// ═══════════════════════════════════════════════════════════════════

let mlLangActual = currentLang;
let mlCargada    = false;
let mlDatosCache = null;

const ML_I18N = {
  es: {
    langLabel:   "Consultar ontología en:",
    statClases:  "Clases",  statObj: "Prop. Objeto",  statDato: "Prop. Dato",  statIndiv: "Individuos",
    titleClases: "📦 Clases OWL",
    titleObj:    "🔗 Propiedades de Objeto",
    titleDato:   "🏷 Propiedades de Dato",
    titleIndiv:  "🧩 Individuos",
    sinResults:  "Sin resultados para este idioma.",
    dominio:     "Dominio", rango: "Rango", inversa: "Inversa",
    padre:       "Subclase de", sinComentario: "Sin descripción.",
    verSparql:   "{ } Ver SPARQL",
  },
  en: {
    langLabel:   "Query ontology in:",
    statClases:  "Classes", statObj: "Obj. Properties", statDato: "Data Properties", statIndiv: "Individuals",
    titleClases: "📦 OWL Classes",
    titleObj:    "🔗 Object Properties",
    titleDato:   "🏷 Data Properties",
    titleIndiv:  "🧩 Individuals",
    sinResults:  "No results for this language.",
    dominio:     "Domain", rango: "Range", inversa: "Inverse",
    padre:       "Subclass of", sinComentario: "No description.",
    verSparql:   "{ } View SPARQL",
  },
  pt: {
    langLabel:   "Consultar ontologia em:",
    statClases:  "Classes", statObj: "Prop. Objeto", statDato: "Prop. Dado", statIndiv: "Indivíduos",
    titleClases: "📦 Classes OWL",
    titleObj:    "🔗 Propriedades de Objeto",
    titleDato:   "🏷 Propriedades de Dado",
    titleIndiv:  "🧩 Indivíduos",
    sinResults:  "Sem resultados para este idioma.",
    dominio:     "Domínio", rango: "Alcance", inversa: "Inversa",
    padre:       "Subclasse de", sinComentario: "Sem descrição.",
    verSparql:   "{ } Ver SPARQL",
  },
};
function ml(key) { return (ML_I18N[mlLangActual] || ML_I18N.es)[key] || key; }

async function mlCargar(lang) {
  mlLangActual = lang;
  document.querySelectorAll(".ml-lang-btn").forEach(b =>
    b.classList.toggle("active", b.dataset.mlang === lang));

  const lbl = document.getElementById("mlLangLabel");
  if (lbl) lbl.textContent = ml("langLabel");
  const ids = {
    mlStatClases: "statClases", mlStatObj: "statObj", mlStatDato: "statDato", mlStatIndiv: "statIndiv",
    mlTitleClases: "titleClases", mlTitlePropsObj: "titleObj", mlTitlePropsDato: "titleDato", mlTitleIndividuos: "titleIndiv",
  };
  Object.entries(ids).forEach(([id, key]) => {
    const el = document.getElementById(id); if (el) el.textContent = ml(key);
  });

  const loader  = document.getElementById("mlLoader");
  const content = document.getElementById("mlContent");
  loader.style.display  = "flex";
  content.style.display = "none";

  try {
    const res  = await fetch(`/api/ontologia/etiquetas?lang=${lang}`);
    const data = await res.json();
    mlDatosCache = data;

    document.getElementById("mlTotalClases").textContent = data.totales.clases;
    document.getElementById("mlTotalObj").textContent    = data.totales.propiedades_objeto;
    document.getElementById("mlTotalDato").textContent   = data.totales.propiedades_dato;
    const indivEl = document.getElementById("mlTotalIndiv");
    if (indivEl) indivEl.textContent = data.totales.individuos || 0;

    const sparqlBase = (tipo) =>
      `PREFIX owl:  <http://www.w3.org/2002/07/owl#>\n` +
      `PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n` +
      `SELECT ?entidad ?label ?comment WHERE {\n` +
      `  ?entidad a owl:${tipo} .\n` +
      `  OPTIONAL { ?entidad rdfs:label   ?label   . FILTER(lang(?label)   = "${lang}") }\n` +
      `  OPTIONAL { ?entidad rdfs:comment ?comment . FILTER(lang(?comment) = "${lang}") }\n` +
      `} ORDER BY ?entidad`;
    document.getElementById("sparqlClases").textContent    = sparqlBase("Class");
    document.getElementById("sparqlPropsObj").textContent  = sparqlBase("ObjectProperty");
    document.getElementById("sparqlPropsDato").textContent = sparqlBase("DatatypeProperty");
    const sparqlIndiv = document.getElementById("sparqlIndividuos");
    if (sparqlIndiv) sparqlIndiv.textContent =
      `PREFIX owl:  <http://www.w3.org/2002/07/owl#>\n` +
      `PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n` +
      `SELECT ?entidad ?label ?comment ?tipo WHERE {\n` +
      `  ?entidad a owl:NamedIndividual .\n` +
      `  OPTIONAL { ?entidad rdfs:label   ?label   . FILTER(lang(?label)   = "${lang}") }\n` +
      `  OPTIONAL { ?entidad rdfs:comment ?comment . FILTER(lang(?comment) = "${lang}") }\n` +
      `  OPTIONAL { ?entidad a ?tipo . FILTER(?tipo != owl:NamedIndividual) }\n` +
      `} ORDER BY ?tipo ?entidad`;
    document.querySelectorAll(".sparql-code").forEach(el => el.classList.remove("open"));

    mlRenderTodo(data);
    loader.style.display  = "none";
    mlCargada = true;
    content.style.display = "block";

  } catch (e) {
    loader.style.display = "none";
    document.getElementById("mlContent").innerHTML =
      `<p style="text-align:center;color:var(--muted);padding:2rem;font-family:'Space Mono',monospace;font-size:0.8rem">
        ⚠️ Error al consultar la ontología. Verificá que Flask esté corriendo.
      </p>`;
    document.getElementById("mlContent").style.display = "block";
  }
}

function toggleMlSparql(id) {
  const el = document.getElementById(id); if (el) el.classList.toggle("open");
}

function mlRenderTodo(data) {
  mlRenderClases(data.clases || []);
  mlRenderPropsAgrupadas("mlPropsObj",  data.propiedades_objeto || [], true);
  mlRenderPropsAgrupadas("mlPropsDato", data.propiedades_dato   || [], false);
  mlRenderIndividuos(data.individuos || []);
}

const ML_ORDEN_CLASES  = ["Celular","Procesador","Memoria","Bateria","Pantalla",
  "CamaraTrasera","CamaraFrontal","Camara","SistemaOperativo",
  "Audio","RedMovil","RedInalambrica","Sensor","Resistencia","TipoSIM"];
const ML_ORDEN_DOMINIO = ["Celular","Procesador","Memoria","Bateria","Pantalla",
  "CamaraTrasera","CamaraFrontal","SistemaOperativo",
  "Audio","RedMovil","RedInalambrica","Sensor","Resistencia","TipoSIM"];

function mlRenderClases(items) {
  const el = document.getElementById("mlClases");
  if (!items.length) {
    el.innerHTML = `<div class="no-results-q">${ml("sinResults")}</div>`;
    return;
  }
  const ordenados = [
    ...ML_ORDEN_CLASES.map(n => items.find(i => i.nombre === n)).filter(Boolean),
    ...items.filter(i => !ML_ORDEN_CLASES.includes(i.nombre)).sort((a,b)=>a.label.localeCompare(b.label)),
  ];
  el.innerHTML = ordenados.map(item => {
    const padreHtml = item.padre
      ? `<div class="ml-card-meta"><span class="ml-badge-mini ml-badge-padre">↑ ${ml("padre")}: ${item.padre}</span></div>`
      : "";
    return `<div class="ml-card ml-card-clase">
      <div class="ml-card-label">${item.label}</div>
      <div class="ml-card-uri">${item.nombre}</div>
      ${padreHtml}
      <div class="ml-card-comment">${item.comment || `<em style="opacity:.5">${ml("sinComentario")}</em>`}</div>
    </div>`;
  }).join("");
}

function mlRenderPropsAgrupadas(containerId, items, esObjeto) {
  const el = document.getElementById(containerId);
  if (!items.length) {
    el.innerHTML = `<div class="no-results-q">${ml("sinResults")}</div>`;
    return;
  }
  const grupos = {}; const sinDominio = [];
  for (const item of items) {
    item.dominio ? (grupos[item.dominio] = grupos[item.dominio] || []).push(item) : sinDominio.push(item);
  }
  const gruposOrdenados = [
    ...ML_ORDEN_DOMINIO.filter(d => grupos[d]),
    ...Object.keys(grupos).filter(d => !ML_ORDEN_DOMINIO.includes(d)).sort(),
  ];
  let html = "";
  for (const dominio of gruposOrdenados) {
    const propsGrupo = grupos[dominio].sort((a,b)=>a.label.localeCompare(b.label));
    html += `<div class="ml-grupo">
      <div class="ml-grupo-titulo">
        <span class="ml-grupo-dominio">${dominio}</span>
        <span class="ml-grupo-count">${propsGrupo.length}</span>
      </div>
      <div class="ml-grid">${propsGrupo.map(i => mlCardProp(i, esObjeto)).join("")}</div>
    </div>`;
  }
  if (sinDominio.length) {
    html += `<div class="ml-grupo">
      <div class="ml-grupo-titulo"><span class="ml-grupo-dominio">—</span><span class="ml-grupo-count">${sinDominio.length}</span></div>
      <div class="ml-grid">${sinDominio.sort((a,b)=>a.label.localeCompare(b.label)).map(i=>mlCardProp(i,esObjeto)).join("")}</div>
    </div>`;
  }
  el.innerHTML = html;
}

function mlCardProp(item, esObjeto) {
  const meta = [];
  if (item.dominio) meta.push(`<span class="ml-badge-mini ml-badge-dom">${ml("dominio")}: ${item.dominio}</span>`);
  if (item.rango)   meta.push(`<span class="ml-badge-mini ml-badge-ran">${ml("rango")}: ${item.rango}</span>`);
  if (item.inversa) meta.push(`<span class="ml-badge-mini ml-badge-inv">⇄ ${ml("inversa")}: ${item.inversa}</span>`);
  const tipoBadge = esObjeto
    ? `<span class="ml-type-badge ml-type-obj">ObjectProperty</span>`
    : `<span class="ml-type-badge ml-type-dato">DatatypeProperty</span>`;
  return `<div class="ml-card ml-card-prop">
    <div class="ml-card-top-row">${tipoBadge}</div>
    <div class="ml-card-label">${item.label}</div>
    <div class="ml-card-uri">${item.nombre}</div>
    ${meta.length ? `<div class="ml-card-meta">${meta.join("")}</div>` : ""}
    <div class="ml-card-comment">${item.comment || `<em style="opacity:.5">${ml("sinComentario")}</em>`}</div>
  </div>`;
}

function mlRenderIndividuos(items) {
  const el = document.getElementById("mlIndividuos");
  if (!el) return;
  if (!items.length) {
    el.innerHTML = `<div class="no-results-q">${ml("sinResults")}</div>`;
    return;
  }
  // Group by tipo (class)
  const grupos = {}; const sinTipo = [];
  for (const item of items) {
    item.tipo ? (grupos[item.tipo] = grupos[item.tipo] || []).push(item) : sinTipo.push(item);
  }
  const gruposOrdenados = [
    ...ML_ORDEN_DOMINIO.filter(d => grupos[d]),
    ...Object.keys(grupos).filter(d => !ML_ORDEN_DOMINIO.includes(d)).sort(),
  ];
  let html = "";
  for (const tipo of gruposOrdenados) {
    const grp = grupos[tipo].sort((a,b)=>a.label.localeCompare(b.label));
    html += `<div class="ml-grupo">
      <div class="ml-grupo-titulo">
        <span class="ml-grupo-dominio">${tipo}</span>
        <span class="ml-grupo-count">${grp.length}</span>
      </div>
      <div class="ml-grid">${grp.map(item => `<div class="ml-card ml-card-indiv">
        <div class="ml-card-top-row"><span class="ml-type-badge ml-type-indiv">Individual</span></div>
        <div class="ml-card-label">${item.label}</div>
        <div class="ml-card-uri">${item.nombre}</div>
        <div class="ml-card-comment">${item.comment || `<em style="opacity:.5">${ml("sinComentario")}</em>`}</div>
      </div>`).join("")}</div>
    </div>`;
  }
  if (sinTipo.length) {
    html += `<div class="ml-grupo">
      <div class="ml-grupo-titulo"><span class="ml-grupo-dominio">—</span><span class="ml-grupo-count">${sinTipo.length}</span></div>
      <div class="ml-grid">${sinTipo.sort((a,b)=>a.label.localeCompare(b.label)).map(item => `<div class="ml-card ml-card-indiv">
        <div class="ml-card-top-row"><span class="ml-type-badge ml-type-indiv">Individual</span></div>
        <div class="ml-card-label">${item.label}</div>
        <div class="ml-card-uri">${item.nombre}</div>
        <div class="ml-card-comment">${item.comment || `<em style="opacity:.5">${ml("sinComentario")}</em>`}</div>
      </div>`).join("")}</div>
    </div>`;
  }
  el.innerHTML = html;
}

// ═══════════════════════════════════════════════════════════════════
// 5. INIT
// ═══════════════════════════════════════════════════════════════════

navigateTo(getHash(), false);

// Apply saved language and setup lang buttons
document.querySelectorAll(".lang-btn").forEach(btn => {
  btn.addEventListener("click", () => applyLang(btn.dataset.lang));
});
applyLang(currentLang);