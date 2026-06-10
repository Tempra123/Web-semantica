// ── consultas.js ─────────────────────────────────────────────────────────────

let consultasCargadas = false;
let todasLasConsultas = [];
let categoriaActiva   = null;
let currentSparql     = "";

// Cargar al entrar a la página
window.addEventListener("DOMContentLoaded", cargarConsultas);

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

    // Botón "Todas"
    const btnTodas = document.createElement("button");
    btnTodas.className = "cat-btn active";
    btnTodas.innerHTML = `<span>Todas</span><span class="cat-badge">${todasLasConsultas.length}</span>`;
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

// Búsqueda en el listado de consultas
document.getElementById("querySearch").addEventListener("input", function () {
  const term = this.value.toLowerCase().trim();
  const base = categoriaActiva
    ? todasLasConsultas.filter(q => q.categoria === categoriaActiva)
    : todasLasConsultas;
  const filtradas = term
    ? base.filter(q =>
        q.titulo.toLowerCase().includes(term) ||
        q.descripcion.toLowerCase().includes(term))
    : base;
  renderQueryList(filtradas);
});

async function ejecutarConsulta(id) {
  const panel      = document.getElementById("resultPanel");
  const rpTitle    = document.getElementById("rpTitle");
  const rpDesc     = document.getElementById("rpDesc");
  const rpBody     = document.getElementById("rpBody");
  const sparqlCode = document.getElementById("sparqlCode");

  panel.classList.add("visible");
  rpTitle.textContent = "Ejecutando consulta...";
  rpDesc.textContent  = "";
  rpBody.innerHTML    = `<div style="padding:1.5rem;text-align:center;color:var(--muted);font-family:'Space Mono',monospace;font-size:0.8rem;"><span class="dot-anim">Consultando ontología</span></div>`;
  sparqlCode.classList.remove("open");

  panel.scrollIntoView({ behavior: "smooth", block: "start" });

  try {
    const res  = await fetch(`/api/consulta/${id}`);
    const data = await res.json();

    rpTitle.textContent = `#${String(data.id).padStart(2, "0")} — ${data.titulo}`;
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
      const metaHtml = `<div class="rp-meta"><span class="rp-count">${total} fila${total !== 1 ? "s" : ""} devuelta${total !== 1 ? "s" : ""}</span></div>`;
      if (total === 0) {
        rpBody.innerHTML = metaHtml + `<div class="no-results-q">La consulta no devolvió resultados en esta ontología.</div>`;
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
  document.getElementById("sparqlCode").classList.toggle("open");
}