import "./styles.css";

const tokenKey = "auto-service-admin-token";
const loginCard = document.querySelector("#login-card");
const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const loginError = document.querySelector("#login-error");
const registerError = document.querySelector("#register-error");
const panel = document.querySelector("#panel");
const page = document.querySelector("#admin-page");
const sessionText = document.querySelector("#session-text");
const logoutButton = document.querySelector("#logout");
const serviceRows = document.querySelector("#service-rows");
const serviceEmpty = document.querySelector("#service-empty");
const serviceError = document.querySelector("#service-error");
const serviceStatus = document.querySelector("#service-status");
const serviceName = document.querySelector("#service-name");
const serviceMin = document.querySelector("#service-min");
const serviceMax = document.querySelector("#service-max");
const serviceAdd = document.querySelector("#service-add");
const serviceSave = document.querySelector("#service-save");
const serviceDelete = document.querySelector("#service-delete");
const statsOpen = document.querySelector("#stats-open");
const statsModal = document.querySelector("#stats-modal");
const statsClose = document.querySelector("#stats-close");
const statsPeriods = document.querySelector("#stats-periods");
const statsError = document.querySelector("#stats-error");
const statsNote = document.querySelector("#stats-note");
const heatmap = document.querySelector("#heatmap");
const heatmapEmpty = document.querySelector("#heatmap-empty");
const queueSummary = document.querySelector("#queue-summary");
const queueRows = document.querySelector("#queue-rows");
const queueEmpty = document.querySelector("#queue-empty");
const queueError = document.querySelector("#queue-error");
const leadModal = document.querySelector("#lead-modal");
const leadClose = document.querySelector("#lead-close");
const leadPlace = document.querySelector("#lead-place");
const leadName = document.querySelector("#lead-name");
const leadTemp = document.querySelector("#lead-temp");
const leadMain = document.querySelector("#lead-main");
const leadReasons = document.querySelector("#lead-reasons");
const leadSpend = document.querySelector("#lead-spend");
const leadDepartment = document.querySelector("#lead-department");
const leadManager = document.querySelector("#lead-manager");
const leadFacts = document.querySelector("#lead-facts");
const leadContacts = document.querySelector("#lead-contacts");

let services = [];
let selectedId = null;

function showError(node, message) {
  node.hidden = !message;
  node.textContent = message || "";
}

async function errorText(response) {
  const data = await response.json().catch(() => ({}));
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]) {
    return String(data.detail[0].msg || "Проверьте поля").replace(/^Value error,\s*/i, "");
  }
  return "Запрос не прошёл";
}

function token() {
  return localStorage.getItem(tokenKey) || "";
}

function showPanel(admin) {
  loginCard.hidden = true;
  panel.hidden = false;
  page.classList.remove("page-narrow");
  page.classList.add("page-desk");
  sessionText.textContent = `Вы вошли как ${admin.login}.`;
  loadServices();
  loadQueue();
}

function showLogin() {
  panel.hidden = true;
  loginCard.hidden = false;
  page.classList.add("page-narrow");
  page.classList.remove("page-desk");
}

function authHeaders() {
  return {
    Authorization: `Bearer ${token()}`,
    "Content-Type": "application/json",
  };
}

function money(value) {
  return `${Number(value).toLocaleString("ru-RU")}\u00a0₽`;
}

function showStatus(message) {
  serviceStatus.hidden = !message;
  serviceStatus.textContent = message || "";
}

function scrollToRow() {
  const row = serviceRows.querySelector("tr.selected") || serviceRows.lastElementChild;
  if (row) row.scrollIntoView({ block: "nearest" });
}

function digits(raw) {
  const text = String(raw).replace(/[^\d]/g, "");
  if (!text) return null;
  return Number(text);
}

function readServiceForm() {
  const name = serviceName.value.trim();
  const budgetMin = digits(serviceMin.value);
  const budgetMax = digits(serviceMax.value);
  if (!name) return { error: "Напишите название услуги." };
  if (budgetMin === null || budgetMax === null) return { error: "Бюджет — два числа: от и до." };
  if (budgetMax < budgetMin) return { error: "Сумма «до» меньше суммы «от»." };
  return { value: { service_name: name, budget_min: budgetMin, budget_max: budgetMax } };
}

function fillServiceForm(row) {
  serviceName.value = row ? row.service_name : "";
  serviceMin.value = row ? String(row.budget_min) : "";
  serviceMax.value = row ? String(row.budget_max) : "";
}

function renderServices() {
  serviceRows.replaceChildren();
  serviceEmpty.hidden = services.length > 0;
  for (const row of services) {
    const tr = document.createElement("tr");
    if (row.id === selectedId) tr.classList.add("selected");
    tr.dataset.id = String(row.id);
    for (const text of [row.id, row.service_name, money(row.budget_min), money(row.budget_max)]) {
      const cell = document.createElement("td");
      cell.textContent = text;
      tr.append(cell);
    }
    serviceRows.append(tr);
  }
}

async function loadServices() {
  showError(serviceError, "");
  try {
    const response = await fetch("/admin-data");
    if (!response.ok) {
      showError(serviceError, "Список услуг не открылся");
      return;
    }
    const data = await response.json();
    if (!Array.isArray(data)) {
      showError(serviceError, "Сервер прислал не список услуг");
      return;
    }
    services = data;
    if (!services.some((row) => row.id === selectedId)) selectedId = null;
    renderServices();
  } catch {
    showError(serviceError, "Сервер не ответил");
  }
}

function selectedService() {
  return services.find((row) => row.id === selectedId) || null;
}

async function sendService(method, path, body) {
  const response = await fetch(path, {
    method,
    headers: authHeaders(),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (response.status === 401) {
    localStorage.removeItem(tokenKey);
    showLogin();
    showError(loginError, "Сессия закончилась, войдите снова");
    return null;
  }
  if (!response.ok) {
    showError(serviceError, await errorText(response));
    return null;
  }
  return response.json();
}

async function loadSession() {
  const saved = token();
  if (!saved) return false;
  const response = await fetch("/auth/me", {
    headers: { Authorization: `Bearer ${saved}` },
  });
  if (!response.ok) {
    localStorage.removeItem(tokenKey);
    return false;
  }
  showPanel(await response.json());
  return true;
}

async function refreshRegister() {
  const response = await fetch("/auth/check");
  if (!response.ok) {
    showError(loginError, "Не удалось проверить, есть ли уже мастер");
    return;
  }
  const data = await response.json();
  registerForm.hidden = Boolean(data.has_admin);
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showError(loginError, "");
  const body = {
    login: new FormData(loginForm).get("login"),
    password: new FormData(loginForm).get("password"),
  };
  const button = loginForm.querySelector("button");
  button.disabled = true;
  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      showError(loginError, await errorText(response));
      return;
    }
    const data = await response.json();
    localStorage.setItem(tokenKey, data.access_token);
    showPanel(data.admin);
    await refreshRegister();
  } catch {
    showError(loginError, "Сервер не ответил");
  } finally {
    button.disabled = false;
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showError(registerError, "");
  const body = {
    login: new FormData(registerForm).get("login"),
    password: new FormData(registerForm).get("password"),
  };
  const button = registerForm.querySelector("button");
  button.disabled = true;
  try {
    const response = await fetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      showError(registerError, await errorText(response));
      await refreshRegister();
      return;
    }
    const data = await response.json();
    localStorage.setItem(tokenKey, data.access_token);
    registerForm.hidden = true;
    showPanel(data.admin);
  } catch {
    showError(registerError, "Сервер не ответил");
  } finally {
    button.disabled = false;
  }
});

logoutButton.addEventListener("click", async () => {
  localStorage.removeItem(tokenKey);
  loginForm.reset();
  selectedId = null;
  fillServiceForm(null);
  showLogin();
  await refreshRegister();
});

serviceRows.addEventListener("click", (event) => {
  const row = event.target.closest("tr");
  if (!row) return;
  selectedId = Number(row.dataset.id);
  fillServiceForm(selectedService());
  showError(serviceError, "");
  renderServices();
});

serviceAdd.addEventListener("click", async () => {
  showError(serviceError, "");
  const form = readServiceForm();
  if (form.error) {
    showError(serviceError, form.error);
    return;
  }
  serviceAdd.disabled = true;
  try {
    const created = await sendService("POST", "/admin-data", form.value);
    if (!created) return;
    selectedId = created.id;
    fillServiceForm(created);
    await loadServices();
    showStatus(`«${created.service_name}» записана. Строка выделена в таблице.`);
    scrollToRow();
  } catch {
    showError(serviceError, "Сервер не ответил");
  } finally {
    serviceAdd.disabled = false;
  }
});

serviceSave.addEventListener("click", async () => {
  showError(serviceError, "");
  if (!selectedService()) {
    showError(serviceError, "Сначала выберите строку в таблице.");
    return;
  }
  const form = readServiceForm();
  if (form.error) {
    showError(serviceError, form.error);
    return;
  }
  serviceSave.disabled = true;
  try {
    const saved = await sendService("PUT", `/admin-data/${selectedId}`, form.value);
    if (!saved) return;
    selectedId = saved.id;
    fillServiceForm(saved);
    await loadServices();
    showStatus(`«${saved.service_name}» обновлена.`);
    scrollToRow();
  } catch {
    showError(serviceError, "Сервер не ответил");
  } finally {
    serviceSave.disabled = false;
  }
});

serviceDelete.addEventListener("click", async () => {
  showError(serviceError, "");
  const current = selectedService();
  if (!current) {
    showError(serviceError, "Сначала выберите строку в таблице.");
    return;
  }
  if (!window.confirm(`Удалить услугу «${current.service_name}»?`)) return;
  serviceDelete.disabled = true;
  try {
    const removed = await sendService("DELETE", `/admin-data/${selectedId}`);
    if (!removed) return;
    selectedId = null;
    fillServiceForm(null);
    await loadServices();
    showStatus(`«${current.service_name}» удалена.`);
  } catch {
    showError(serviceError, "Сервер не ответил");
  } finally {
    serviceDelete.disabled = false;
  }
});

async function start() {
  await refreshRegister();
  await loadSession();
}

function duration(seconds) {
  const value = Math.max(0, Math.round(Number(seconds) || 0));
  if (value < 60) return `${value} с`;
  const minutes = Math.floor(value / 60);
  const rest = value % 60;
  return rest ? `${minutes} мин ${rest} с` : `${minutes} мин`;
}

function unlockPage() {
  if (statsModal.hidden && leadModal.hidden) document.body.style.overflow = "";
}

function closeStats() {
  statsModal.hidden = true;
  unlockPage();
}

const tempClass = {
  "горячая": "temp temp-hot",
  "тёплая": "temp temp-warm",
  "холодная": "temp temp-cold",
};

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text;
  return td;
}

function renderQueue(data) {
  const items = Array.isArray(data.items) ? data.items : [];
  queueSummary.replaceChildren();
  for (const [title, value] of [
    ["Всего", data.total],
    ["Горячие", data.hot],
    ["Тёплые", data.warm],
    ["Холодные", data.cold],
    ["С менеджером", data.with_manager],
  ]) {
    const card = document.createElement("article");
    card.className = "stats-card";
    const titleNode = document.createElement("span");
    titleNode.textContent = title;
    const valueNode = document.createElement("strong");
    valueNode.textContent = String(value ?? 0);
    card.append(titleNode, valueNode);
    queueSummary.append(card);
  }

  queueRows.replaceChildren();
  queueEmpty.hidden = items.length > 0;
  for (const item of items) {
    const row = document.createElement("tr");
    row.append(
      cell(item.place),
      cell(item.full_name),
    );
    const temperature = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = tempClass[item.temperature] || "temp";
    badge.textContent = item.temperature || "";
    temperature.append(badge);
    const action = document.createElement("td");
    const view = document.createElement("button");
    view.type = "button";
    view.className = "ghost";
    view.textContent = "Просмотр";
    view.addEventListener("click", (event) => {
      event.stopPropagation();
      openLead(item);
    });
    action.append(view);
    row.append(
      temperature,
      cell(item.deadline || "—"),
      cell(item.department || "—"),
      cell(item.personal_manager ? "да" : "нет"),
      action,
    );
    row.addEventListener("click", () => openLead(item));
    queueRows.append(row);
  }
}

async function loadQueue() {
  showError(queueError, "");
  try {
    const response = await fetch("/leads/queue");
    if (!response.ok) {
      showError(queueError, "Очередь заявок не открылась");
      return;
    }
    renderQueue(await response.json());
  } catch {
    showError(queueError, "Сервер не ответил");
  }
}

function fact(label, value, wide) {
  if (!String(value || "").trim()) return null;
  const box = document.createElement("div");
  if (wide) box.className = "lead-wide";
  const title = document.createElement("span");
  title.textContent = label;
  const text = document.createElement("p");
  text.textContent = value;
  box.append(title, text);
  return box;
}

function contactLink(label, href, text) {
  if (href) {
    const link = document.createElement("a");
    link.className = "contact-pill";
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = `${label}: ${text}`;
    return link;
  }
  const note = document.createElement("span");
  note.className = "contact-pill";
  note.textContent = `${label}: ${text}`;
  return note;
}

function openLead(item) {
  leadPlace.textContent = `Место ${item.place || ""}`;
  leadName.textContent = item.full_name || "Заявка";
  leadTemp.className = tempClass[item.temperature] || "temp";
  leadTemp.textContent = item.temperature || "";
  leadMain.textContent = item.main_reason || "";
  leadReasons.replaceChildren();
  for (const reason of item.reasons || []) {
    const line = document.createElement("li");
    line.textContent = reason;
    leadReasons.append(line);
  }
  leadSpend.textContent = item.spend_time || "";
  leadDepartment.textContent = item.department || "";
  leadManager.textContent = item.manager_text || "";

  leadFacts.replaceChildren();
  const facts = [
    fact("Услуга", item.product),
    fact("Срок", item.deadline),
    fact("Бюджет", item.budget),
    fact("Ниша", item.business_niche),
    fact("О бизнесе", item.business_info, true),
    fact("Размер компании", item.company_size),
    fact("Размер бизнеса", item.business_size),
    fact("Объём задачи", item.task_volume),
    fact("Объём потребности", item.need_volume),
    fact("Кто заполнил", item.client_role),
    fact("Тип задачи", item.task_type),
    fact("Как связаться", item.contact_method),
    fact("Удобное время", item.convenient_time),
    fact("Комментарий", item.comment, true),
  ];
  for (const node of facts) {
    if (node) leadFacts.append(node);
  }

  leadContacts.replaceChildren();
  const phone = String(item.phone || "").trim();
  const email = String(item.email || "").trim();
  const telegram = String(item.telegram || "").trim().replace(/^@/, "");
  const whatsapp = String(item.whatsapp || "").replace(/\D/g, "");
  const maxContact = String(item.max_contact || "").trim();
  if (phone) leadContacts.append(contactLink("Телефон", `tel:${phone.replace(/[^\d+]/g, "")}`, phone));
  if (email.includes("@")) leadContacts.append(contactLink("Почта", `mailto:${email}`, email));
  if (/^[\w]{3,}$/.test(telegram)) {
    leadContacts.append(contactLink("Telegram", `https://t.me/${telegram}`, `@${telegram}`));
  }
  if (whatsapp.length >= 10) {
    leadContacts.append(contactLink("WhatsApp", `https://wa.me/${whatsapp}`, item.whatsapp));
  }
  if (maxContact) leadContacts.append(contactLink("Макс", "", maxContact));
  if (!leadContacts.childElementCount) {
    const empty = document.createElement("p");
    empty.className = "fine";
    empty.textContent = "Контактов в заявке нет.";
    leadContacts.append(empty);
  }

  leadModal.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeLead() {
  leadModal.hidden = true;
  unlockPage();
}

function drawHeatmap(data) {
  heatmap.replaceChildren();
  const points = Array.isArray(data.points) ? data.points : [];
  heatmapEmpty.hidden = points.length > 0;
  if (!points.length) return;
  const width = 1000;
  const height = 640;
  const maxX = Math.max(1, Number(data.max_x) || 1);
  const maxY = Math.max(1, Number(data.max_y) || 1);
  const maxCount = Math.max(...points.map((point) => point.count));
  const svg = "http://www.w3.org/2000/svg";
  for (const point of points) {
    const circle = document.createElementNS(svg, "circle");
    const scale = point.count / maxCount;
    circle.setAttribute("cx", String((point.x / maxX) * (width - 48) + 24));
    circle.setAttribute("cy", String((point.y / maxY) * (height - 48) + 24));
    circle.setAttribute("r", String(7 + scale * 26));
    circle.setAttribute("fill", `rgba(228, 201, 138, ${0.28 + scale * 0.62})`);
    heatmap.append(circle);
  }
}

function renderStats(data) {
  statsPeriods.replaceChildren();
  const periods = Array.isArray(data.periods) ? data.periods : [];
  for (const period of periods) {
    const card = document.createElement("article");
    card.className = "stats-card";
    const title = document.createElement("span");
    title.textContent = period.title;
    const average = document.createElement("strong");
    average.textContent = period.visits ? duration(period.average_seconds) : "нет визитов";
    const detail = document.createElement("p");
    detail.textContent = period.visits
      ? `дольше всего ${duration(period.max_seconds)}, визитов ${period.visits}`
      : "за этот срок страницу заявки не открывали";
    card.append(title, average, detail);
    statsPeriods.append(card);
  }
  const filled = periods.filter((period) => period.visits);
  const same = filled.length > 1 && filled.every((period) => period.average_seconds === filled[0].average_seconds);
  statsNote.hidden = !same;
  statsNote.textContent = "Пока все заходы свежие, сутки, неделя и месяц показывают одно и то же.";
  drawHeatmap(data);
}

async function openStats() {
  statsModal.hidden = false;
  document.body.style.overflow = "hidden";
  showError(statsError, "");
  statsPeriods.replaceChildren();
  heatmap.replaceChildren();
  try {
    const response = await fetch("/behavior-metrics/summary");
    if (!response.ok) {
      showError(statsError, "Статистика не открылась");
      return;
    }
    renderStats(await response.json());
  } catch {
    showError(statsError, "Сервер не ответил");
  }
}

statsOpen.addEventListener("click", openStats);
statsClose.addEventListener("click", closeStats);
statsModal.addEventListener("click", (event) => {
  if (event.target === statsModal) closeStats();
});
leadClose.addEventListener("click", closeLead);
leadModal.addEventListener("click", (event) => {
  if (event.target === leadModal) closeLead();
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (!leadModal.hidden) {
    closeLead();
    return;
  }
  if (!statsModal.hidden) closeStats();
});

start();
