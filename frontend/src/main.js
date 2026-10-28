import "./styles.css";

const contactMethods = [
  { name: "Телефон", placeholder: "+7 900 000-00-00", column: "phone" },
  { name: "Почта", placeholder: "name@example.com", column: "email" },
  { name: "Telegram", placeholder: "@username", column: "telegram" },
  { name: "WhatsApp", placeholder: "Номер или имя", column: "whatsapp" },
  { name: "Макс", placeholder: "Имя или номер в Макс", column: "max_contact" },
];

const form = document.querySelector("#lead-form");
const productSelect = document.querySelector("#product");
const productName = document.querySelector("#product-name");
const budgetFrom = document.querySelector("#budget-from");
const budgetTo = document.querySelector("#budget-to");
const errorBox = document.querySelector("#form-error");
const submitButton = document.querySelector("#submit");
const thanks = document.querySelector("#thanks");
const thanksText = document.querySelector("#thanks-text");
const contactList = document.querySelector("#contacts");
const addContactButton = document.querySelector("#add-contact");

const startedAt = Date.now();
const clicks = [];
const pauses = [];
const buttonCounts = new Map();
const services = new Map();
let cursorX = 0;
let cursorY = 0;
let cursorSeen = false;
let behaviorSending = false;

const visitKey = "auto-service-visits";
const visits = Number(localStorage.getItem(visitKey) || "0") + 1;
localStorage.setItem(visitKey, String(visits));
const returnCount = Math.max(0, visits - 1);

document.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  const name = button.dataset.track || button.textContent.trim();
  clicks.push(name);
  buttonCounts.set(name, (buttonCounts.get(name) || 0) + 1);
});

let pauseTimer = 0;
let lastX = 0;
let lastY = 0;
document.addEventListener("mousemove", (event) => {
  cursorX = event.clientX;
  cursorY = event.clientY;
  cursorSeen = true;
  const dx = event.clientX - lastX;
  const dy = event.clientY - lastY;
  if (dx * dx + dy * dy < 64) return;
  lastX = event.clientX;
  lastY = event.clientY;
  window.clearTimeout(pauseTimer);
  pauseTimer = window.setTimeout(() => {
    const element = document.elementFromPoint(lastX, lastY);
    const field = element && element.closest("[data-field]");
    const name = field ? field.dataset.field : "фон";
    pauses.push(`${name} ${Math.round(lastX)},${Math.round(lastY)}`);
    if (pauses.length > 12) pauses.shift();
  }, 800);
});

function money(value) {
  return `${Number(value).toLocaleString("ru-RU")} ₽`;
}

function buttonSummary() {
  return [...buttonCounts.entries()].map(([name, count]) => `${name} × ${count}`).join(", ");
}

async function sendBehavior() {
  if (document.hidden || behaviorSending) return;
  behaviorSending = true;
  const point = cursorSeen ? `${Math.round(cursorX)},${Math.round(cursorY)}` : "0,0";
  try {
    await fetch("/behavior-metrics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        application_id: 0,
        time_on_page: Math.max(0, Math.round((Date.now() - startedAt) / 1000)),
        buttons_clicked: buttonSummary(),
        cursor_positions: point,
        return_frequency: 0,
      }),
    });
  } catch {
    // Статистика не должна мешать заявке.
  } finally {
    behaviorSending = false;
  }
}

window.setInterval(sendBehavior, 1000);

productSelect.addEventListener("change", () => {
  if (productSelect.value) productName.value = productSelect.value;
});

function parseMoney(raw) {
  const digits = String(raw).replace(/[^\d]/g, "");
  if (!digits) return null;
  return Number(digits);
}

function budgetText() {
  const from = parseMoney(budgetFrom.value);
  const to = parseMoney(budgetTo.value);
  if (from === null || to === null) {
    return { error: "Укажите бюджет двумя числами: от и до. Пробелы можно ставить." };
  }
  if (to < from) return { error: "Сумма «до» меньше суммы «от»." };
  return { value: `от ${money(from)} до ${money(to)}` };
}

function fillServices(rows) {
  services.clear();
  for (const row of rows) {
    const name = String(row.service_name || "").trim();
    if (!name) continue;
    const current = services.get(name);
    const min = Number(row.budget_min) || 0;
    const max = Number(row.budget_max) || 0;
    if (!current) {
      services.set(name, { name, min, max });
    } else {
      current.min = Math.min(current.min, min);
      current.max = Math.max(current.max, max);
    }
  }

  productSelect.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = services.size === 0 ? "Список пуст, напишите свою" : "Не обязательно";
  productSelect.append(placeholder);
  for (const service of services.values()) {
    const option = document.createElement("option");
    option.value = service.name;
    option.textContent = service.name;
    productSelect.append(option);
  }
  productSelect.disabled = services.size === 0;
}

async function loadServices() {
  try {
    const response = await fetch("/admin-data");
    if (!response.ok) throw new Error(String(response.status));
    fillServices(await response.json());
  } catch {
    productSelect.replaceChildren();
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "Список недоступен, напишите свою";
    productSelect.append(option);
    productSelect.disabled = true;
  }
}

function addContactRow() {
  const row = document.createElement("div");
  row.className = "contact-row";

  const methodLabel = document.createElement("label");
  methodLabel.className = "field";
  const methodCaption = document.createElement("span");
  methodCaption.textContent = "Способ связи";
  const method = document.createElement("select");
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Выберите";
  method.append(placeholder);
  for (const item of contactMethods) {
    const option = document.createElement("option");
    option.value = item.name;
    option.textContent = item.name;
    method.append(option);
  }

  const valueLabel = document.createElement("label");
  valueLabel.className = "field";
  const valueCaption = document.createElement("span");
  valueCaption.textContent = "Контакт";
  const value = document.createElement("input");
  value.type = "text";
  value.placeholder = "Номер или имя";

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "ghost";
  remove.dataset.track = "убрать способ связи";
  remove.textContent = "Убрать";

  method.addEventListener("change", () => {
    const item = contactMethods.find((entry) => entry.name === method.value);
    value.placeholder = item ? item.placeholder : "Номер или имя";
  });
  remove.addEventListener("click", () => {
    row.remove();
    refreshContactRows();
  });

  methodLabel.append(methodCaption, method);
  valueLabel.append(valueCaption, value);
  row.append(methodLabel, valueLabel, remove);
  contactList.append(row);
  refreshContactRows();
}

function refreshContactRows() {
  const rows = contactList.querySelectorAll(".contact-row");
  rows.forEach((row) => {
    row.querySelector("button").hidden = rows.length === 1;
  });
}

function collectContacts() {
  const grouped = {
    phone: [],
    email: [],
    telegram: [],
    whatsapp: [],
    max_contact: [],
  };
  const pairs = [];
  for (const row of contactList.querySelectorAll(".contact-row")) {
    const method = row.querySelector("select").value.trim();
    const value = row.querySelector("input").value.trim();
    if (!value && !method) continue;
    const item = contactMethods.find((entry) => entry.name === method);
    if (item && value) grouped[item.column].push(value);
    if (value) pairs.push(method ? `${method}: ${value}` : value);
    else pairs.push(method);
  }
  return {
    contact_method: pairs.join("; "),
    phone: grouped.phone.join(", "),
    email: grouped.email.join(", "),
    telegram: grouped.telegram.join(", "),
    whatsapp: grouped.whatsapp.join(", "),
    max_contact: grouped.max_contact.join(", "),
  };
}

function fieldValue(name) {
  const value = new FormData(form).get(name);
  return typeof value === "string" ? value.trim() : "";
}

function showError(message) {
  errorBox.hidden = false;
  errorBox.textContent = message;
  errorBox.scrollIntoView({ block: "nearest" });
}

function techNote() {
  const screen = `${window.screen.width}x${window.screen.height}`;
  const zone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
  return `screen=${screen}; lang=${navigator.language || ""}; tz=${zone}`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.hidden = true;

  if (!fieldValue("first_name") || !fieldValue("last_name")) {
    showError("Укажите имя и фамилию.");
    return;
  }
  const product = productName.value.trim() || productSelect.value.trim();
  if (!product) {
    showError("Напишите услугу или выберите её из списка.");
    return;
  }
  const budget = budgetText();
  if (budget.error) {
    showError(budget.error);
    return;
  }
  const contacts = collectContacts();

  const payload = {
    first_name: fieldValue("first_name"),
    last_name: fieldValue("last_name"),
    middle_name: fieldValue("middle_name"),
    business_info: fieldValue("business_info"),
    budget: budget.value,
    contact_method: contacts.contact_method,
    phone: contacts.phone,
    email: contacts.email,
    telegram: contacts.telegram,
    whatsapp: contacts.whatsapp,
    max_contact: contacts.max_contact,
    comment: fieldValue("comment"),
    business_niche: fieldValue("business_niche"),
    company_size: fieldValue("company_size"),
    task_volume: fieldValue("task_volume"),
    client_role: fieldValue("client_role"),
    business_size: fieldValue("business_size"),
    need_volume: fieldValue("need_volume"),
    deadline: fieldValue("deadline"),
    task_type: fieldValue("task_type"),
    product,
    convenient_time: fieldValue("convenient_time"),
  };

  submitButton.disabled = true;
  submitButton.textContent = "Отправляем";

  try {
    const leadResponse = await fetch("/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!leadResponse.ok) throw new Error("lead");
    const lead = await leadResponse.json();

    const pauseText = pauses.join("; ");
    await fetch("/lead-metrics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lead_id: lead.id,
        time_on_page: Math.max(0, Math.round((Date.now() - startedAt) / 1000)),
        buttons_clicked: clicks.join(", "),
        cursor_pauses: [pauseText, techNote()].filter(Boolean).join(" | "),
        return_count: returnCount,
      }),
    });

    form.hidden = true;
    thanks.hidden = false;
    thanksText.textContent = `${payload.first_name}, заявка на «${payload.product}» записана. Бюджет ${payload.budget}. Мы свяжемся способом «${payload.contact_method}».`;
  } catch {
    showError("Заявку не удалось записать. Попробуйте ещё раз.");
    submitButton.disabled = false;
    submitButton.textContent = "Отправить заявку";
  }
});

addContactButton.addEventListener("click", addContactRow);
addContactRow();
loadServices();
