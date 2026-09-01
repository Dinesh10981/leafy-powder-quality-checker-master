const API_BASE = new URLSearchParams(window.location.search).get("api") ||
  (window.location.protocol === "file:" ? "http://localhost:5050" : window.location.origin);
const BANDS = [["R", "val-610"], ["S", "val-680"], ["T", "val-730"], ["U", "val-760"], ["V", "val-810"], ["W", "val-860"]];
const sensorInputs = BANDS.map(([, id]) => document.getElementById(id));
const liveIndex = document.getElementById("live-index");

let sensorHistory = [];
let scanInProgress = false;
let autoScanTimer = null;
let currentRecord = null;

function showToast(message, icon = "check_circle", isError = false) {
  const toast = document.getElementById("toast");
  document.getElementById("toast-msg").textContent = message;
  document.getElementById("toast-icon").textContent = icon;
  toast.style.background = isError ? "#ba1a1a" : (icon === "warning" ? "#855300" : "#006b2c");
  toast.style.opacity = "1";
  toast.style.transform = "translateY(0)";
  window.setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(12px)";
  }, 3600);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[character]);
}

async function api(path, options = {}) {
  const response = await fetch(API_BASE + path, { cache: "no-store", ...options });
  let payload = {};
  try {
    payload = await response.json();
  } catch (_error) {
    payload = { error: "Sensor service returned an invalid response." };
  }
  if (!response.ok || payload.ok === false) {
    throw new Error(payload.error || `Request failed (${response.status})`);
  }
  return payload;
}

function sampleId(record) {
  return `MOR-${String(record.sample_no).padStart(5, "0")}`;
}

function renderHistory() {
  const body = document.getElementById("history-tbody");
  const empty = document.getElementById("history-empty");
  const count = document.getElementById("history-count");
  count.textContent = `${sensorHistory.length} record${sensorHistory.length === 1 ? "" : "s"}`;
  if (!sensorHistory.length) {
    body.innerHTML = "";
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";
  body.innerHTML = sensorHistory.map((record, index) => {
    const badge = record.quality === "Good" ? "badge-good" : (record.quality === "Moderate" ? "badge-moderate" : "badge-poor");
    return `<tr class="hover:bg-surface transition-colors">
      <td class="px-6 py-4" style="color:#3e4a3d">${escapeHtml(`${record.date} ${record.time}`)}</td>
      <td class="px-6 py-4 font-mono font-semibold text-xs">${escapeHtml(sampleId(record))}</td>
      <td class="px-6 py-4 text-right font-bold">${Number(record.lpqi).toFixed(3)}</td>
      <td class="px-6 py-4"><span class="badge ${badge}">${escapeHtml(record.quality)}</span></td>
      <td class="px-6 py-4 text-right"><button onclick="viewReading(${index})" class="text-xs font-semibold hover:underline" style="color:#006b2c;background:none;border:none;cursor:pointer;font-family:inherit">View</button></td>
    </tr>`;
  }).join("");
}

function fillInputs(record) {
  BANDS.forEach(([band, id]) => {
    document.getElementById(id).value = Number(record[band]).toFixed(4);
  });
  liveIndex.textContent = Number(record.lpqi).toFixed(3);
  liveIndex.style.color = record.lpqi >= 0.45 ? "#006b2c" : (record.lpqi >= 0.25 ? "#855300" : "#bb0112");
}

function setResult(state, record) {
  const accent = document.getElementById("result-accent");
  const iconContainer = document.getElementById("result-icon-container");
  const icon = document.getElementById("result-icon");
  const title = document.getElementById("result-title");
  const description = document.getElementById("result-desc");
  const metrics = document.getElementById("result-metrics");
  const indexValue = document.getElementById("final-index");
  icon.classList.remove("animate-spin");

  if (state === "idle") {
    accent.style.background = "#bdcaba";
    iconContainer.style.background = "#eceef0";
    iconContainer.style.boxShadow = "";
    icon.textContent = "hourglass_empty";
    icon.style.color = "#bdcaba";
    title.textContent = "Awaiting Sensor";
    title.style.color = "#3e4a3d";
    description.textContent = "Start the sensor service, then scan once or enable automatic collection.";
    description.style.color = "#6e7b6c";
    metrics.style.display = "none";
    currentRecord = null;
    return;
  }

  if (state === "loading") {
    accent.style.background = "linear-gradient(90deg,#bdcaba,#006b2c,#bdcaba)";
    icon.textContent = "autorenew";
    icon.classList.add("animate-spin");
    icon.style.color = "#006b2c";
    title.textContent = "Scanning Sensor…";
    title.style.color = "#191c1e";
    description.textContent = "Collecting all six bands, calculating LPQI, and saving the record to Excel…";
    description.style.color = "#3e4a3d";
    return;
  }

  const styles = {
    good: { accent: "linear-gradient(90deg,#006b2c,#62df7d)", background: "rgba(0,107,44,0.1)", color: "#006b2c", icon: "check_circle", title: "Good Quality", description: "Strong NIR response relative to the red edge produced a high LPQI." },
    moderate: { accent: "linear-gradient(90deg,#fea619,#ffb95f)", background: "rgba(254,166,25,0.12)", color: "#684000", icon: "warning", title: "Moderate Quality", description: "The red-edge/NIR contrast is intermediate; validate this sample against calibrated references." },
    poor: { accent: "linear-gradient(90deg,#bb0112,#e02928)", background: "rgba(187,1,18,0.08)", color: "#bb0112", icon: "error", title: "Poor Quality", description: "The spectral curve has low red-edge/NIR contrast, producing a low LPQI." },
  };
  const selected = styles[state];
  accent.style.background = selected.accent;
  iconContainer.style.background = selected.background;
  iconContainer.style.boxShadow = state === "good" ? "0 0 24px rgba(0,107,44,0.18)" : "";
  icon.textContent = selected.icon;
  icon.style.color = selected.color;
  title.textContent = selected.title;
  title.style.color = selected.color;
  description.textContent = selected.description;
  description.style.color = "#3e4a3d";
  metrics.style.display = "block";
  indexValue.textContent = Number(record.lpqi).toFixed(3);
  indexValue.style.color = selected.color;
  document.getElementById("red-edge-val").textContent = Number(record.red_edge_average).toFixed(2);
  document.getElementById("nir-val").textContent = Number(record.nir_average).toFixed(2);
  document.getElementById("sample-id").textContent = sampleId(record);
  currentRecord = record;
  updateExplanation();
}

function setConnection(online, title, detail) {
  document.getElementById("sensor-dot").style.background = online ? "#006b2c" : "#bb0112";
  document.getElementById("sensor-status").textContent = title;
  document.getElementById("sensor-detail").textContent = detail;
}

async function scanSensor() {
  if (scanInProgress) return;
  scanInProgress = true;
  const button = document.getElementById("predict-btn");
  const label = document.getElementById("predict-label");
  const icon = document.getElementById("predict-icon");
  label.textContent = "Scanning…";
  icon.textContent = "autorenew";
  icon.classList.add("animate-spin");
  button.disabled = true;
  setResult("loading", null);
  try {
    const record = await api("/api/scan", { method: "POST" });
    fillInputs(record);
    setResult(record.quality.toLowerCase(), record);
    sensorHistory = [record, ...sensorHistory].slice(0, 500);
    renderHistory();
    showToast(`Sample ${record.sample_no} saved: ${record.quality} quality.`, record.quality === "Good" ? "check_circle" : (record.quality === "Moderate" ? "warning" : "error"));
    setConnection(true, "Sensor service online", `Last sample saved at ${record.time}`);
  } catch (error) {
    setResult("idle", null);
    setConnection(false, "Sensor unavailable", error.message);
    showToast(error.message, "error", true);
  } finally {
    icon.classList.remove("animate-spin");
    label.textContent = "Scan Sensor & Analyze";
    icon.textContent = "sensors";
    button.disabled = false;
    scanInProgress = false;
  }
}

function viewReading(index) {
  const record = sensorHistory[index];
  fillInputs(record);
  setResult(record.quality.toLowerCase(), record);
  document.getElementById("spectral-form").scrollIntoView({ behavior: "smooth", block: "center" });
}

async function loadHistory() {
  try {
    const result = await api("/api/history");
    sensorHistory = result.rows || [];
    renderHistory();
  } catch (error) {
    sensorHistory = [];
    renderHistory();
    setConnection(false, "Start data_logger.py", error.message);
  }
}

async function clearHistory() {
  if (!sensorHistory.length || !window.confirm("Delete all saved sensor readings from the Excel workbook?")) return;
  try {
    await api("/api/history", { method: "DELETE" });
    sensorHistory = [];
    renderHistory();
    setResult("idle", null);
    sensorInputs.forEach((input) => { input.value = ""; });
    liveIndex.textContent = "--";
    showToast("Excel history cleared.", "delete");
  } catch (error) {
    showToast(error.message, "error", true);
  }
}

function downloadExcel() {
  if (!sensorHistory.length) {
    showToast("No sensor records to download.", "warning", true);
    return;
  }
  window.location.href = `${API_BASE}/api/export`;
}

async function loadStatus(showSuccess = false) {
  try {
    const status = await api("/api/status");
    const detail = status.last_scan_ok === false ? status.last_scan_error : `${status.samples} saved sample${status.samples === 1 ? "" : "s"} · ${status.sensor_url}`;
    setConnection(status.last_scan_ok !== false, "Sensor service online", detail);
    if (showSuccess) showToast("Sensor service is reachable.");
  } catch (error) {
    setConnection(false, "Start data_logger.py", error.message);
    if (showSuccess) showToast(error.message, "error", true);
  }
}

function updateExplanation() {
  const explanation = document.getElementById("explanation-text");
  const detailed = document.getElementById("ai-toggle").checked;
  if (detailed && currentRecord) {
    explanation.innerHTML = `<p><strong>Calculation trace:</strong> Red-edge average = (680 + 730) / 2 = ${Number(currentRecord.red_edge_average).toFixed(4)}. NIR average = (760 + 810 + 860) / 3 = ${Number(currentRecord.nir_average).toFixed(4)}. LPQI = (NIR − red-edge) / (NIR + red-edge) = ${Number(currentRecord.lpqi).toFixed(4)}.</p>`;
    explanation.style.background = "rgba(0,107,44,0.04)";
    explanation.style.borderColor = "rgba(0,107,44,0.2)";
  } else {
    explanation.innerHTML = '<p class="mb-2"><strong>Standard Model:</strong> LPQI is a normalized difference contrasting the average of the 680 and 730 nm red-edge bands against the average of the 760, 810, and 860 nm NIR bands.</p><p>The 610 nm band is retained in every record for diagnostics and future calibration, but it is not part of the documented LPQI equation.</p>';
    explanation.style.background = "#f7f9fb";
    explanation.style.borderColor = "#eceef0";
  }
}

function showComingSoon(event) {
  event.preventDefault();
  showToast("Coming soon!", "schedule");
}

document.getElementById("predict-btn").addEventListener("click", scanSensor);
document.getElementById("reset-btn").addEventListener("click", () => {
  sensorInputs.forEach((input) => { input.value = ""; });
  liveIndex.textContent = "--";
  liveIndex.style.color = "#bdcaba";
  setResult("idle", null);
});
document.getElementById("auto-scan").addEventListener("change", (event) => {
  if (event.target.checked) {
    scanSensor();
    autoScanTimer = window.setInterval(scanSensor, 5000);
    showToast("Automatic sensor collection enabled.", "sensors");
  } else {
    window.clearInterval(autoScanTimer);
    autoScanTimer = null;
    showToast("Automatic collection stopped.", "pause");
  }
});
document.getElementById("ai-toggle").addEventListener("change", updateExplanation);

renderHistory();
setResult("idle", null);
updateExplanation();
loadStatus();
loadHistory();
window.setInterval(() => loadStatus(false), 5000);
