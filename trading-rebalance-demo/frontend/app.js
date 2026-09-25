"use strict";

const $ = (id) => document.getElementById(id);
const state = { plan: null, polling: null };

const usd = (v) => Number(v).toLocaleString("en-US", { style: "currency", currency: "USD" });
const pct = (v, signed = false) => {
  const n = Number(v);
  const s = n.toFixed(2) + "%";
  return signed && n > 0 ? "+" + s : s;
};
const qty = (v) => Number(v).toLocaleString("en-US", { maximumFractionDigits: 8 });
const badge = (text) => `<span class="badge ${text}">${text}</span>`;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `${res.status} ${res.statusText}`);
  return body;
}

// ---------------------------------------------------------------- portfolio

async function loadPortfolio() {
  const p = await api("/portfolio");
  $("pv").textContent = `· ${usd(p.portfolio_value)}`;
  $("current-body").innerHTML = p.holdings.map((h) => `
    <tr>
      <td><strong>${esc(h.asset)}</strong></td>
      <td class="num">${qty(h.quantity)}</td>
      <td class="num">${usd(h.price)}</td>
      <td class="num">${usd(h.value)}</td>
      <td class="num">${pct(h.pct)}</td>
    </tr>`).join("");
  $("target-body").innerHTML = Object.entries(p.target_allocation).map(([asset, t]) => `
    <tr>
      <td><strong>${esc(asset)}</strong></td>
      <td class="num">${pct(t)}</td>
      <td><div class="bar"><span style="width:${Math.min(100, t)}%"></span></div></td>
    </tr>`).join("");
}

async function checkHealth() {
  try {
    const h = await api("/health");
    $("health").textContent = `API ${h.status} · ${h.exchange} exchange`;
    $("health").classList.add("ok");
  } catch {
    $("health").textContent = "API unreachable";
  }
}

// ---------------------------------------------------------------- rebalance

async function calculate() {
  $("calc-btn").disabled = true;
  try {
    const plan = await api("/rebalance", { method: "POST", body: "{}" });
    state.plan = plan;
    renderPlan(plan);
  } catch (err) {
    alert(`Rebalance failed: ${err.message}`);
  } finally {
    $("calc-btn").disabled = false;
  }
}

function renderPlan(plan) {
  $("plan-id").textContent = `· ${plan.plan_id}`;
  $("plan-body").innerHTML = plan.rows.map((r) => {
    const cls = r.diff_pct > 0 ? "pos" : r.diff_pct < 0 ? "neg" : "";
    const isQuote = r.action === "QUOTE";
    return `
      <tr>
        <td><strong>${esc(r.asset)}</strong></td>
        <td class="num">${pct(r.current_pct)}</td>
        <td class="num">${pct(r.target_pct)}</td>
        <td class="num ${cls}">${pct(r.diff_pct, true)}</td>
        <td>${badge(r.action)}${isQuote ? ' <span class="muted">settlement</span>' : ""}</td>
        <td class="num">${r.action === "HOLD" ? "—" : qty(r.quantity)}</td>
        <td class="num">${r.action === "HOLD" ? "—" : usd(r.estimated_value)}</td>
      </tr>`;
  }).join("");

  const sells = plan.orders.filter((o) => o.side === "SELL").length;
  const buys = plan.orders.length - sells;
  const notes = [`${plan.orders.length} order(s): ${sells} SELL, ${buys} BUY. SELLs are submitted first so their proceeds fund the BUYs.`];
  $("plan-warnings").innerHTML =
    `<p class="muted">${notes.join(" ")}</p>` +
    plan.warnings.map((w) => `<p class="warn">⚠ ${esc(w)}</p>`).join("");

  const select = $("reject-select");
  const prev = select.value || "SOL";
  select.innerHTML = '<option value="">None</option>' +
    plan.orders.map((o) => `<option value="${esc(o.asset)}">${esc(o.symbol)}</option>`).join("");
  select.value = plan.orders.some((o) => o.asset === prev) ? prev : "";

  $("approve-btn").disabled = plan.orders.length === 0;
}

// ---------------------------------------------------------------- execution

async function approve() {
  if (!state.plan) return;
  $("approve-btn").disabled = true;
  $("calc-btn").disabled = true;
  try {
    const result = await api("/orders/execute", {
      method: "POST",
      body: JSON.stringify({
        plan_id: state.plan.plan_id,
        simulate_rejection_asset: $("reject-select").value || null,
      }),
    });
    renderExecution(result.orders, result.summary, false);
    startPolling(result.plan_id);
  } catch (err) {
    alert(`Execution failed: ${err.message}`);
    $("calc-btn").disabled = false;
  }
}

function startPolling(planId) {
  clearInterval(state.polling);
  state.polling = setInterval(async () => {
    const { orders, summary } = await api(`/orders?plan_id=${encodeURIComponent(planId)}`);
    const done = summary.PENDING === 0;
    renderExecution(orders, summary, done);
    await loadHistory();
    if (done) {
      clearInterval(state.polling);
      state.polling = null;
      $("calc-btn").disabled = false;
      await loadPortfolio();
    }
  }, 700);
}

function renderExecution(orders, summary, done) {
  const parts = Object.entries(summary).map(([s, n]) => `${badge(s)}${n}`).join(" &nbsp; ");
  $("exec-summary").classList.remove("muted");
  $("exec-summary").innerHTML = `${parts} &nbsp; <span class="muted">${
    done ? "Execution complete — current portfolio updated from mock exchange balances."
         : "Waiting for mock exchange to settle orders…"}</span>`;
  $("exec-body").innerHTML = orders.map((o) => `
    <tr>
      <td class="mono">${esc(o.order_id)}</td>
      <td class="mono">${esc(o.exchange_order_id || "—")}</td>
      <td>${esc(o.symbol)}</td>
      <td>${badge(o.side)}</td>
      <td class="num">${qty(o.quantity)}</td>
      <td class="num">${o.average_price ? usd(o.average_price) : "—"}</td>
      <td class="num">${o.status === "FILLED" ? usd(o.fee) : "—"}</td>
      <td>${badge(o.status)}</td>
      <td class="muted">${esc(o.reject_reason || (o.status === "FILLED" ? `Filled ${qty(o.filled_quantity)}` : ""))}</td>
    </tr>`).join("");
}

async function loadHistory() {
  const { orders } = await api("/orders");
  if (!orders.length) {
    $("history-body").innerHTML = '<tr><td colspan="8" class="muted">No orders yet.</td></tr>';
    return;
  }
  $("history-body").innerHTML = orders.slice().reverse().map((o) => `
    <tr>
      <td>${new Date(o.created_at).toISOString().replace("T", " ").slice(0, 19)}</td>
      <td class="mono">${esc(o.plan_id)}</td>
      <td class="mono">${esc(o.order_id)}</td>
      <td>${esc(o.symbol)}</td>
      <td>${badge(o.side)}</td>
      <td class="num">${qty(o.quantity)}</td>
      <td class="num">${usd(o.estimated_value)}</td>
      <td>${badge(o.status)}</td>
    </tr>`).join("");
}

async function resetDemo() {
  clearInterval(state.polling);
  state.plan = null;
  await api("/demo/reset", { method: "POST" });
  $("plan-id").textContent = "";
  $("plan-body").innerHTML = '<tr><td colspan="7" class="muted">Click “Calculate Rebalance” to generate orders.</td></tr>';
  $("plan-warnings").innerHTML = "";
  $("approve-btn").disabled = true;
  $("calc-btn").disabled = false;
  $("exec-summary").className = "summary muted";
  $("exec-summary").textContent = "No orders submitted yet.";
  $("exec-body").innerHTML = "";
  await Promise.all([loadPortfolio(), loadHistory()]);
}

$("calc-btn").addEventListener("click", calculate);
$("approve-btn").addEventListener("click", approve);
$("reset-btn").addEventListener("click", resetDemo);

checkHealth();
loadPortfolio();
loadHistory();
