const API = "";

async function apiGet(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`Falha em ${path}: ${res.status}`);
  return res.json();
}

async function checkHealth() {
  const el = document.getElementById("conn-status");
  try {
    await apiGet("/api/health");
    el.textContent = "API conectada";
    el.classList.add("ok");
  } catch (e) {
    el.textContent = "API indisponível";
    el.classList.add("error");
  }
}

async function loadKpis() {
  const data = await apiGet("/api/dashboard/summary");
  document.getElementById("kpi-stores").textContent = data.total_stores;
  document.getElementById("kpi-products").textContent = data.total_products;
  document.getElementById("kpi-critical").textContent = data.critical_items;
  document.getElementById("kpi-critical-pct").textContent = `${data.critical_pct}%`;
}

async function loadStoresAndProducts() {
  const [stores, products] = await Promise.all([apiGet("/api/stores"), apiGet("/api/products")]);

  const retailStores = stores.filter((s) => !s.is_distribution_center);

  const storeSelect = document.getElementById("select-store");
  const inventoryStoreSelect = document.getElementById("select-inventory-store");
  const productSelect = document.getElementById("select-product");

  storeSelect.innerHTML = retailStores.map((s) => `<option value="${s.id}">${s.name} — ${s.city}</option>`).join("");
  inventoryStoreSelect.innerHTML =
    `<option value="">Todas as lojas</option>` +
    retailStores.map((s) => `<option value="${s.id}">${s.name} — ${s.city}</option>`).join("");
  productSelect.innerHTML = products.map((p) => `<option value="${p.id}">${p.name}</option>`).join("");
}

// Gráfico de linha desenhado direto em <canvas>, sem dependências externas
// (mantém a demo funcionando mesmo sem acesso a uma CDN de terceiros).
function renderForecastChart(labelsHistory, historyValues, labelsForecast, forecastValues) {
  const canvas = document.getElementById("forecast-chart");
  const wrap = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  const cssWidth = wrap.clientWidth || 480;
  const cssHeight = wrap.clientHeight || 300;

  canvas.width = cssWidth * dpr;
  canvas.height = cssHeight * dpr;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, cssWidth, cssHeight);

  if (historyValues.length === 0) return;

  const allLabels = [...labelsHistory, ...labelsForecast];
  const maxVal = Math.max(...historyValues, ...forecastValues, 1) * 1.15;

  const padding = { left: 36, right: 12, top: 30, bottom: 34 };
  const plotW = cssWidth - padding.left - padding.right;
  const plotH = cssHeight - padding.top - padding.bottom;
  const n = allLabels.length;
  const stepX = n > 1 ? plotW / (n - 1) : 0;

  const xAt = (i) => padding.left + stepX * i;
  const yAt = (v) => padding.top + plotH - (v / maxVal) * plotH;

  // grade horizontal
  ctx.strokeStyle = "#e5e9e5";
  ctx.fillStyle = "#5b665e";
  ctx.font = "11px sans-serif";
  ctx.lineWidth = 1;
  const gridSteps = 4;
  for (let g = 0; g <= gridSteps; g++) {
    const v = (maxVal / gridSteps) * g;
    const y = yAt(v);
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(cssWidth - padding.right, y);
    ctx.stroke();
    ctx.fillText(String(Math.round(v)), 2, y + 3);
  }

  // rótulos do eixo X (amostrados para não sobrepor)
  const maxLabels = Math.max(1, Math.floor(plotW / 55));
  const labelStep = Math.max(1, Math.ceil(n / maxLabels));
  ctx.textAlign = "right";
  for (let i = 0; i < n; i += labelStep) {
    const x = xAt(i);
    ctx.save();
    ctx.translate(x, cssHeight - padding.bottom + 14);
    ctx.rotate(-Math.PI / 5);
    ctx.fillText(allLabels[i].slice(5), 0, 0);
    ctx.restore();
  }
  ctx.textAlign = "left";

  // linha de historico (verde, solida)
  ctx.strokeStyle = "#1f7a3f";
  ctx.lineWidth = 2;
  ctx.beginPath();
  historyValues.forEach((v, i) => {
    const x = xAt(i), y = yAt(v);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = "#1f7a3f";
  historyValues.forEach((v, i) => {
    ctx.beginPath();
    ctx.arc(xAt(i), yAt(v), 2.5, 0, Math.PI * 2);
    ctx.fill();
  });

  // linha de previsao (dourada, tracejada), a partir do ultimo ponto historico
  const startIdx = historyValues.length - 1;
  ctx.strokeStyle = "#c9a227";
  ctx.setLineDash([6, 4]);
  ctx.beginPath();
  ctx.moveTo(xAt(startIdx), yAt(historyValues[startIdx]));
  forecastValues.forEach((v, i) => ctx.lineTo(xAt(startIdx + 1 + i), yAt(v)));
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "#c9a227";
  forecastValues.forEach((v, i) => {
    ctx.beginPath();
    ctx.arc(xAt(startIdx + 1 + i), yAt(v), 2.5, 0, Math.PI * 2);
    ctx.fill();
  });

  // legenda
  ctx.font = "12px sans-serif";
  ctx.fillStyle = "#1f7a3f";
  ctx.fillRect(padding.left, 4, 10, 10);
  ctx.fillStyle = "#1a1f1a";
  ctx.fillText("Vendas históricas", padding.left + 14, 13);
  ctx.fillStyle = "#c9a227";
  ctx.fillRect(padding.left + 140, 4, 10, 10);
  ctx.fillStyle = "#1a1f1a";
  ctx.fillText("Previsão (Holt)", padding.left + 154, 13);
}

async function runForecast() {
  const storeId = document.getElementById("select-store").value;
  const productId = document.getElementById("select-product").value;
  const horizon = document.getElementById("input-horizon").value || 7;
  if (!storeId || !productId) return;

  const data = await apiGet(`/api/forecast/${storeId}/${productId}?horizon_days=${horizon}`);

  const historyLabels = data.history.map((h) => h.day);
  const historyValues = data.history.map((h) => h.units_sold);
  const forecastLabels = data.forecast.map((f) => f.day);
  const forecastValues = data.forecast.map((f) => f.forecast_units);

  renderForecastChart(historyLabels, historyValues, forecastLabels, forecastValues);

  document.getElementById("f-avg").textContent = data.avg_daily_demand;
  document.getElementById("f-stock").textContent = data.current_stock;
  document.getElementById("f-suggested").textContent = data.suggested_replenishment;
  document.getElementById("f-risk").textContent = data.stockout_risk_days ?? "—";
}

async function runRoutePlan() {
  const data = await apiGet("/api/logistics/route-plan");

  const summary = document.getElementById("route-summary");
  summary.classList.remove("hidden");
  document.getElementById("r-origin").textContent = data.origin;
  document.getElementById("r-total").textContent = data.total_distance_km;
  document.getElementById("r-naive").textContent = data.naive_distance_km;
  document.getElementById("r-saved").textContent = `${data.distance_saved_km} km (${data.distance_saved_pct}%)`;

  const list = document.getElementById("route-list");
  if (data.stops.length === 0) {
    list.innerHTML = `<li>Nenhuma loja em estoque crítico no momento — nenhuma entrega necessária.</li>`;
    return;
  }

  list.innerHTML = data.stops
    .map(
      (s) => `<li>
        <span><span class="stop-order">${s.order}</span>${s.store_name} — ${s.city}</span>
        <span>${s.distance_from_previous_km} km · ${s.units_to_deliver} un.</span>
      </li>`
    )
    .join("");
}

async function loadInventory() {
  const storeId = document.getElementById("select-inventory-store").value;
  const query = storeId ? `?store_id=${storeId}` : "";
  const data = await apiGet(`/api/inventory${query}`);

  const body = document.getElementById("inventory-body");
  body.innerHTML = data
    .map(
      (i) => `<tr class="${i.status === "critico" ? "critical" : ""}">
        <td>${i.store_name}</td>
        <td>${i.product_name}</td>
        <td>${i.quantity_on_hand}</td>
        <td>${i.reorder_point}</td>
        <td>${i.status === "critico" ? "Crítico" : "OK"}</td>
      </tr>`
    )
    .join("");
}

async function safely(label, fn) {
  try {
    await fn();
  } catch (err) {
    console.error(`Falha ao carregar ${label}:`, err);
  }
}

async function init() {
  await safely("status da API", checkHealth);
  await Promise.all([safely("KPIs", loadKpis), safely("lojas/produtos", loadStoresAndProducts)]);
  await safely("previsão inicial", runForecast);
  await safely("estoque", loadInventory);

  document.getElementById("btn-forecast").addEventListener("click", () => safely("previsão", runForecast));
  document.getElementById("btn-route").addEventListener("click", () => safely("rota", runRoutePlan));
  document.getElementById("select-inventory-store").addEventListener("change", () => safely("estoque", loadInventory));
  window.addEventListener("resize", () => safely("redesenho do gráfico", runForecast));
}

init();
