// ── buscador.js ──────────────────────────────────────────────────────────────

let filtroActivo = "todos";
let debounceTimer;

const grid         = document.getElementById("grid");
const searchInput  = document.getElementById("searchInput");
const resultsCount = document.getElementById("resultsCount");
const loader       = document.getElementById("loader");
const modalBg      = document.getElementById("modalBg");
const modalClose   = document.getElementById("modalClose");
const modalTitle   = document.getElementById("modalTitle");
const modalContent = document.getElementById("modalContent");
const semBadges    = document.getElementById("semanticBadges");

// Filtros por botón de gama
document.querySelectorAll(".filtro-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filtro-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    filtroActivo = btn.dataset.filtro;
    buscar();
  });
});

// Búsqueda con debounce al escribir
searchInput.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(buscar, 350);
});

// Enter para buscar
searchInput.addEventListener("keydown", e => {
  if (e.key === "Enter") { clearTimeout(debounceTimer); buscar(); }
});

// Función usada por los chips de sugerencia
function buscarTermino(termino) {
  searchInput.value = termino;
  buscar();
}

// ── Helpers de renderizado ──────────────────────────────────────────────────

function tagGama(gama) {
  const g = (gama || "").toLowerCase();
  if (g === "alta")  return `<span class="tag tag-gama-alta">Gama Alta</span>`;
  if (g === "media") return `<span class="tag tag-gama-media">Gama Media</span>`;
  if (g === "baja")  return `<span class="tag tag-gama-baja">Gama Baja</span>`;
  return gama !== "—" ? `<span class="tag tag-gama-def">${gama}</span>` : "";
}

function mostrarBadgesSemánticos(filtros) {
  if (!filtros || Object.keys(filtros).length === 0) {
    semBadges.style.display = "none";
    return;
  }
  const items = [];
  if (filtros.gama)  items.push(`Gama: ${filtros.gama}`);
  if (filtros.so)    items.push(`SO: ${filtros.so}`);
  if (filtros.ram)   items.push(`RAM: ${filtros.ram}GB`);

  if (items.length === 0) { semBadges.style.display = "none"; return; }

  semBadges.style.display = "flex";
  semBadges.innerHTML =
    `<span class="sem-label">🧠 Detectado:</span>` +
    items.map(i => `<span class="sem-badge">${i}</span>`).join("");
}

function renderCards(resultados) {
  grid.innerHTML = "";
  if (resultados.length === 0) {
    grid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">📭</div>
        <h3>Sin resultados</h3>
        <p>Probá con otro término o cambiá los filtros</p>
      </div>`;
    return;
  }
  resultados.forEach((c, i) => {
    const div = document.createElement("div");
    div.className = "card";
    div.style.animationDelay = `${i * 0.04}s`;
    const precio = c.precio !== "—"
      ? `<div class="card-precio">$ ${parseFloat(c.precio).toLocaleString()}</div>` : "";
    const ramTag = c.ram  !== "—" ? `<span class="tag tag-ram">${c.ram} GB RAM</span>` : "";
    const soTag  = c.so   !== "—" ? `<span class="tag tag-so">${c.so}</span>` : "";
    div.innerHTML = `
      <div class="card-brand">${c.marca}</div>
      <div class="card-model">${c.modelo}</div>
      <div class="card-tags">${tagGama(c.gama)}${soTag}${ramTag}</div>
      ${precio}`;
    div.addEventListener("click", () => abrirDetalle(c.uri, `${c.marca} ${c.modelo}`));
    grid.appendChild(div);
  });
}

// ── Búsqueda principal ───────────────────────────────────────────────────────

async function buscar() {
  const q = searchInput.value.trim();
  loader.style.display = "block";
  grid.innerHTML = "";
  grid.appendChild(loader);
  semBadges.style.display = "none";

  try {
    const res  = await fetch(`/buscar?q=${encodeURIComponent(q)}&filtro=${filtroActivo}`);
    const data = await res.json();
    resultsCount.textContent = `${data.total} resultado${data.total !== 1 ? "s" : ""}`;
    mostrarBadgesSemánticos(data.filtros_detectados);
    renderCards(data.resultados);
  } catch (e) {
    grid.innerHTML = `
      <div class="empty">
        <div class="empty-icon">⚠️</div>
        <h3>Error de conexión</h3>
        <p>Verificá que Flask esté corriendo en el puerto 5000</p>
      </div>`;
  }
}

// ── Modal: abrir y cerrar ────────────────────────────────────────────────────

function abrirModal() {
  document.body.style.overflow = "hidden";
  modalBg.classList.add("open");
}

function cerrarModal() {
  document.body.style.overflow = "";
  modalBg.classList.remove("open");
}

modalClose.addEventListener("click", cerrarModal);
modalBg.addEventListener("click", e => { if (e.target === modalBg) cerrarModal(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") cerrarModal(); });

// ── Detalle celular (enriquecido con DBpedia) ────────────────────────────────

async function abrirDetalle(uri, titulo) {
  modalTitle.textContent = titulo;
  modalContent.innerHTML = "<p style='color:var(--muted);font-size:0.85rem'>Cargando...</p>";
  modalBg.scrollTop = 0;
  abrirModal();

  try {
    const res  = await fetch(`/detalle/${encodeURIComponent(uri)}`);
    const data = await res.json();

    const dbpedia = data["DBpedia"] || null;
    const keys    = Object.keys(data).filter(k => k !== "type" && k !== "DBpedia");

    if (keys.length === 0 && !dbpedia) {
      modalContent.innerHTML = "<p style='color:var(--muted);font-size:0.85rem'>Sin propiedades adicionales.</p>";
      return;
    }

    // Propiedades locales de la ontología
    let html = keys.map(grupo => {
      const props = data[grupo];
      if (typeof props !== "object") return "";
      const filas = Object.entries(props)
        .map(([p, v]) => `<div class="prop-row"><span class="prop-key">${p}</span><span class="prop-val">${v}</span></div>`)
        .join("");
      return `<div class="detalle-grupo">
        <div class="detalle-grupo-titulo">${grupo}</div>
        ${filas}
      </div>`;
    }).join("");

    // Sección DBpedia
    if (dbpedia && dbpedia.encontrado) {
      const imagen = dbpedia.imagen
        ? `<img src="${dbpedia.imagen}" alt="${titulo}" class="dbpedia-img">`
        : "";
      const enlaceWiki = dbpedia.enlace_wiki
        ? `<a href="${dbpedia.enlace_wiki}" target="_blank" class="dbpedia-link">📖 Ver en Wikipedia</a>`
        : "";
      const enlaceDbp = dbpedia.enlace_dbpedia
        ? `<a href="${dbpedia.enlace_dbpedia}" target="_blank" class="dbpedia-link">🔗 Ver en DBpedia</a>`
        : "";

      html += `
      <div class="detalle-grupo detalle-dbpedia">
        <div class="detalle-grupo-titulo dbpedia-titulo">
          🌐 Información desde DBpedia
          <span class="dbpedia-badge">Base de Conocimiento Remota</span>
        </div>
        <div class="dbpedia-body">
          ${imagen}
          <div class="dbpedia-texto">
            <p class="dbpedia-desc">${dbpedia.descripcion || "Sin descripción disponible."}</p>
            <div class="dbpedia-links">${enlaceWiki} ${enlaceDbp}</div>
          </div>
        </div>
      </div>`;
    } else if (dbpedia && !dbpedia.encontrado) {
      html += `
      <div class="detalle-grupo detalle-dbpedia">
        <div class="detalle-grupo-titulo dbpedia-titulo">
          🌐 DBpedia
          <span class="dbpedia-badge">Base de Conocimiento Remota</span>
        </div>
        <p style="color:var(--muted);font-size:0.83rem;padding:0.5rem 0">
          No se encontró información adicional en DBpedia para este dispositivo.
        </p>
      </div>`;
    }

    modalContent.innerHTML = html;

  } catch (e) {
    modalContent.innerHTML = "<p style='color:var(--muted)'>Error al cargar detalles.</p>";
  }
}

// Cargar al iniciar
buscar();