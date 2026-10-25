// Sentinel demo UI — talks to the FastAPI backend (same origin).
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const api = (path, opts) => fetch(path, opts).then(r => r.json());
const esc = s => String(s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

// ---- tiles: weakness categories ----
const TILES = [
  { tag: "API1", h: "Broken Object Level Authorization", p: "One user reads another's object.", id: "vulnerabilities/bola" },
  { tag: "API2", h: "Broken Authentication", p: "Weak login, tokens and JWT validation.", id: "vulnerabilities/broken_authentication" },
  { tag: "API3", h: "Excessive Data Exposure", p: "Responses leak more than needed.", id: "vulnerabilities/excessive_data_exposure" },
  { tag: "API4", h: "Lack of Rate Limiting", p: "No brake on guessing or scraping.", id: "vulnerabilities/lack_of_rate_limiting" },
  { tag: "API5", h: "Broken Function Level Auth", p: "Low-privilege users hit admin actions.", id: "vulnerabilities/bfla" },
  { tag: "API6", h: "Mass Assignment", p: "Extra fields bound onto objects.", id: "vulnerabilities/mass_assignment" },
  { tag: "API8", h: "Injection", p: "Input reaches a backend interpreter.", id: "vulnerabilities/injection" },
  { tag: "GraphQL", h: "GraphQL Risks", p: "Introspection, IDEs, resolver authz.", id: "vulnerabilities/graphql_attacks" },
];
function renderTiles() {
  $("#tileGrid").innerHTML = TILES.map(t => `
    <div class="tile" data-q="Explain ${esc(t.h)} and how to prevent it.">
      <span class="tag">${esc(t.tag)}</span>
      <h3>${esc(t.h)}</h3><p>${esc(t.p)}</p>
      <span class="go">Ask the assistant ›</span>
    </div>`).join("");
  $$(".tile").forEach(el => el.onclick = () => askInMain(el.dataset.q));
}

// ---- health + trust ----
async function loadHealth() {
  try {
    const h = await api("/api/health");
    $("#healthNote").textContent =
      `Local engine ready · ${h.concepts} concepts · provider: ${h.provider}` +
      (h.provider === "ollama" ? ` (${h.ollama_model})` : "");
    const g = await api("/api/graph");
    $("#trustCount").textContent = `${g.count} concepts`;
    $("#trustLinks").textContent = `${g.link_count} links`;
    renderGraph(g);
  } catch (e) {
    $("#healthNote").textContent = "Backend not reachable — start it with: uv run uvicorn src.api:app";
  }
}

// ---- main assistant ----
async function askInMain(q) {
  if (q) $("#q").value = q;
  const query = $("#q").value.trim();
  if (!query) return;
  const box = $("#answer");
  box.classList.remove("hidden");
  box.innerHTML = `<div class="ans-body"><span class="spin"></span> Retrieving concepts and asking the local model…</div>`;
  document.getElementById("assistant").scrollIntoView({ behavior: "smooth" });
  try {
    const r = await api("/api/chat", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: +$("#topk").value, hop_depth: +$("#hops").value }),
    });
    box.innerHTML = renderAnswer(r);
  } catch (e) {
    box.innerHTML = `<div class="ans-body">Error contacting the backend: ${esc(e.message)}</div>`;
  }
}
function renderAnswer(r) {
  const flags = r.trust_flags.map(f => `<div class="flag">⚠ <code>${esc(f.path)}</code> — ${esc(f.reason)}</div>`).join("");
  const cites = r.citations.map(c => `
    <div class="cite">
      <span class="path">[${esc(c.path)}]</span>
      ${c.seed ? '<span class="badge seed">seed</span>' : ""}
      ${c.trust_tier && c.trust_tier !== "unverified" ? `<span class="badge trust">${esc(c.trust_tier)}</span>` : ""}
      ${c.stale ? '<span class="badge stale">stale</span>' : ""}
      ${c.status === "deprecated" ? '<span class="badge dep">deprecated</span>' : ""}
      <div>${esc(c.title)}</div>
    </div>`).join("");
  const trav = r.traversal.length
    ? `<h4>Graph traversal</h4>` + r.traversal.map(p => `<div class="trav">${esc(p)}</div>`).join("")
    : "";
  return `
    <div class="ans-body">
      <h4>Grounded answer</h4>
      <div class="ans-text">${esc(r.answer)}</div>
    </div>
    <div class="side">
      ${flags ? `<h4>Trust gate</h4>${flags}` : ""}
      <h4>Cited concepts</h4>${cites}
      ${trav}
    </div>`;
}

// ---- demo lab ----
let SCN = {}, curScenario = "bola", curMode = "vulnerable";
const SC_INPUTS = {
  bola: `<label>Signed in as<select data-k="caller"><option>alice</option><option>bob</option></select></label>
         <label>Account ID to request<input data-k="account_id" value="5502" /></label>`,
  auth: `<label>Username<input data-k="username" value="alice" /></label>
         <label>Password guess<input data-k="password" value="wrong-guess" /></label>
         <label><input type="checkbox" data-k="reset" style="width:auto"/> reset attempt counter first</label>`,
  jwt: `<label>Token<select data-k="token" id="jwtSel"></select></label>`,
  mass: `<label>Registration body (JSON)<input data-k="body" value='{"username":"mallory","password":"x","isAdmin":true}' /></label>`,
  injection: `<label>Search value<input data-k="name" value="' OR '1'='1" /></label>`,
};
async function loadScenarios() {
  const d = await api("/api/demo/scenarios");
  SCN = d.scenarios;
  $("#scenarioTabs").innerHTML = Object.entries(SCN).map(([k, v]) =>
    `<button data-k="${k}" class="${k === curScenario ? "active" : ""}">${esc(v.title)}</button>`).join("");
  $$("#scenarioTabs button").forEach(b => b.onclick = () => selectScenario(b.dataset.k));
  selectScenario(curScenario);
}
async function selectScenario(k) {
  curScenario = k;
  $$("#scenarioTabs button").forEach(b => b.classList.toggle("active", b.dataset.k === k));
  $("#scTitle").textContent = SCN[k].title;
  $("#scBlurb").textContent = SCN[k].blurb;
  $("#scInputs").innerHTML = SC_INPUTS[k] || "";
  $("#reqOut").textContent = $("#resOut").textContent = "—";
  $("#verdict").classList.add("hidden");
  if (k === "jwt") {
    const s = await api("/api/demo/jwt/sample");
    $("#jwtSel").innerHTML =
      `<option value="${s.forged_none}">forged alg:none admin token</option>
       <option value="${s.valid_admin}">valid signed admin token</option>`;
  }
}
function collectParams() {
  const p = {};
  $$("#scInputs [data-k]").forEach(el => {
    let v = el.type === "checkbox" ? el.checked : el.value;
    if (el.dataset.k === "body") { try { v = JSON.parse(v); } catch { } }
    if (el.dataset.k === "account_id") v = +v;
    p[el.dataset.k] = v;
  });
  return p;
}
async function runDemo() {
  const r = await api(`/api/demo/${curScenario}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: curMode, params: collectParams() }),
  });
  $("#reqOut").textContent = JSON.stringify(r.request, null, 2);
  $("#resOut").textContent = JSON.stringify(r.response, null, 2);
  const v = $("#verdict");
  v.classList.remove("hidden", "blocked", "exposed");
  v.classList.add(r.attack_blocked ? "blocked" : "exposed");
  v.innerHTML = `<span class="vhead">${r.attack_blocked ? "✓ Secure outcome" : "✗ Exploited"}</span>
    ${esc(r.explanation)}<br><br>Control: <strong>${esc(r.control)}</strong> ·
    <a href="#" data-q="Explain the ${esc(r.control)} control and how it prevents this.">ask the assistant ›</a>`;
  v.querySelector("a").onclick = e => { e.preventDefault(); askInMain(e.target.dataset.q); };
}

// ---- graph ----
function renderGraph(g) {
  const groups = {};
  g.nodes.forEach(n => {
    const grp = n.id.includes("/") ? n.id.split("/")[0] : "root";
    (groups[grp] ||= []).push(n);
  });
  const order = ["api_security", "vulnerabilities", "controls", "runbooks", "standards", "policies", "runbooks/api_testing"];
  const keys = Object.keys(groups).sort((a, b) => (order.indexOf(a) + 1 || 99) - (order.indexOf(b) + 1 || 99));
  $("#graphGroups").innerHTML = keys.map(k => `
    <div class="ggroup"><h3>${esc(k)} (${groups[k].length})</h3><ul>
      ${groups[k].map(n => `<li data-q="Tell me about ${esc(n.title)}.">${esc(n.title)}
        ${n.stale ? '<span class="st">STALE</span>' : ""}
        ${n.status === "deprecated" ? '<span class="st">DEPRECATED</span>' : ""}</li>`).join("")}
    </ul></div>`).join("");
  $$("#graphGroups li").forEach(li => li.onclick = () => askInMain(li.dataset.q));
}

// ---- floating chatbot ----
function addMsg(who, html) {
  const d = document.createElement("div");
  d.className = `msg ${who}`;
  d.innerHTML = html;
  $("#chatLog").append(d);
  $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
  return d;
}
async function chatSend(e) {
  e.preventDefault();
  const t = $("#chatText").value.trim();
  if (!t) return;
  $("#chatText").value = "";
  addMsg("user", esc(t));
  const pend = addMsg("bot", '<span class="spin"></span> thinking…');
  try {
    const r = await api("/api/chat", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: t, top_k: 3, hop_depth: 1 }),
    });
    const cites = r.citations.slice(0, 4).map(c => `<span class="path">[${esc(c.path)}]</span>`).join(" ");
    pend.innerHTML = esc(r.answer) + (cites ? `<br><br>${cites}` : "");
  } catch {
    pend.innerHTML = "Backend not reachable.";
  }
}

// ---- wire up ----
document.addEventListener("DOMContentLoaded", () => {
  renderTiles();
  loadHealth();
  loadScenarios();
  $("#askBtn").onclick = () => askInMain();
  $("#runDemo").onclick = runDemo;
  $$(".mode").forEach(m => m.onclick = () => {
    curMode = m.dataset.mode;
    $$(".mode").forEach(x => x.classList.toggle("active", x === m));
  });
  $("#chatFab").onclick = () => { $("#chatPanel").classList.remove("hidden"); $("#chatFab").classList.add("hidden");
    if (!$("#chatLog").children.length) addMsg("bot", "Hi! Ask me how to keep your API requests secure. Every answer cites the OKF concept it came from."); };
  $("#chatClose").onclick = () => { $("#chatPanel").classList.add("hidden"); $("#chatFab").classList.remove("hidden"); };
  $("#chatForm").onsubmit = chatSend;
  $("#searchBtn").onclick = () => document.getElementById("assistant").scrollIntoView({ behavior: "smooth" });
});
