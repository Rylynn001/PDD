const API_BASE = "http://localhost:8000/api/v1";

const queryBtn  = document.getElementById("queryBtn");
const exportBtn = document.getElementById("exportBtn");
const statusEl  = document.getElementById("status");
const tableWrapper = document.getElementById("tableWrapper");
const totalCount   = document.getElementById("totalCount");
const resultTable  = document.getElementById("resultTable");

let lastPayload = null;

function showStatus(msg, type = "info") {
  statusEl.textContent = msg;
  statusEl.className = `status ${type}`;
}

function getPayload() {
  return {
    anti:       document.getElementById("anti").value.trim(),
    cookie:     document.getElementById("cookie").value.trim(),
    start_date: document.getElementById("startDate").value,
    end_date:   document.getElementById("endDate").value,
  };
}

function validate(payload) {
  if (!payload.anti)       return "请填写 Anti-Content";
  if (!payload.cookie)     return "请填写 Cookie";
  if (!payload.start_date) return "请选择开始日期";
  if (!payload.end_date)   return "请选择结束日期";
  if (payload.start_date > payload.end_date) return "开始日期不能晚于结束日期";
  return null;
}

function renderTable(data) {
  if (!data.length) {
    resultTable.innerHTML = "";
    tableWrapper.classList.add("hidden");
    return;
  }
  const keys = Object.keys(data[0]);
  const thead = `<thead><tr>${keys.map(k => `<th>${k}</th>`).join("")}</tr></thead>`;
  const rows  = data.map(row =>
    `<tr>${keys.map(k => `<td>${row[k] ?? "-"}</td>`).join("")}</tr>`
  ).join("");
  resultTable.innerHTML = `${thead}<tbody>${rows}</tbody>`;
  totalCount.textContent = `共 ${data.length} 条数据`;
  tableWrapper.classList.remove("hidden");
}

queryBtn.addEventListener("click", async () => {
  const payload = getPayload();
  const err = validate(payload);
  if (err) { showStatus(err, "error"); return; }

  showStatus("查询中...", "info");
  queryBtn.disabled = true;
  exportBtn.disabled = true;
  tableWrapper.classList.add("hidden");

  try {
    const resp = await fetch(`${API_BASE}/trade/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await resp.json();
    if (!resp.ok) {
      showStatus(`请求失败：${json.detail ?? resp.status}`, "error");
      return;
    }
    lastPayload = payload;
    renderTable(json.data);
    showStatus(`查询成功，共 ${json.total} 条`, "success");
    exportBtn.disabled = json.total === 0;
  } catch (e) {
    showStatus(`网络错误：${e.message}`, "error");
  } finally {
    queryBtn.disabled = false;
  }
});

exportBtn.addEventListener("click", async () => {
  if (!lastPayload) return;
  exportBtn.disabled = true;
  showStatus("正在导出...", "info");

  try {
    const resp = await fetch(`${API_BASE}/trade/query/excel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastPayload),
    });
    if (!resp.ok) {
      const json = await resp.json();
      showStatus(`导出失败：${json.detail ?? resp.status}`, "error");
      return;
    }
    const blob = await resp.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `pdd_trade_${lastPayload.start_date}_${lastPayload.end_date}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
    showStatus("导出成功", "success");
  } catch (e) {
    showStatus(`网络错误：${e.message}`, "error");
  } finally {
    exportBtn.disabled = false;
  }
});
