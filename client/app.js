const state = {
    user: { name: "Visitor", email: "guest@flowershop.com", role: "Visitor" },
    flowers: [],
    language: localStorage.getItem("language") || "en",
    socket: null,
    hasEntered: false
};

const colorOptions = ["Red", "White", "Blue", "Pink", "Orange", "Indigo", "Yellow", "Purple", "Green"];

const $ = (id) => document.getElementById(id);
const t = (key) => (window.translations[state.language] || window.translations.en)[key] || key;

function applyTranslations() {
    document.documentElement.lang = state.language;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
        el.placeholder = t(el.dataset.i18nPlaceholder);
    });
    $("languageSelect").value = state.language;
    populateColorSelects();
    renderUser();
    renderFlowers();
}

function populateColorSelects() {
    const currentFilter = $("colorFilter").value;
    const currentFlowerColor = $("flowerColor").value;
    $("colorFilter").innerHTML = `<option value="">${t("allColors")}</option>`;
    $("flowerColor").innerHTML = "";
    colorOptions.forEach((color) => {
        $("colorFilter").appendChild(new Option(color, color));
        $("flowerColor").appendChild(new Option(color, color));
    });
    $("colorFilter").value = currentFilter;
    $("flowerColor").value = currentFlowerColor || colorOptions[0];
}

async function api(path, options = {}) {
    const response = await fetch(path, {
        credentials: "include",
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options
    });
    if (!response.ok) {
        let error = { message: "Request failed.", code: "ERROR" };
        try {
            error = await response.json();
        } catch (_) {
            error.message = await response.text();
        }
        throw error;
    }
    const contentType = response.headers.get("content-type") || "";
    return contentType.includes("application/json") ? response.json() : response.text();
}

function showMessage(message, isError = false) {
    const box = $("messageArea");
    box.textContent = message;
    box.classList.toggle("error", isError);
    box.classList.remove("hidden");
    clearTimeout(showMessage.timer);
    showMessage.timer = setTimeout(() => box.classList.add("hidden"), 4500);
}

function renderUser() {
    const label = state.user.role === "Visitor" ? t("visitor") : `${state.user.name} (${state.user.role})`;
    $("currentUser").textContent = label;
    $("logoutBtn").classList.toggle("hidden", !state.hasEntered);
    $("authPanel").classList.toggle("hidden", state.hasEntered);
    $("flowerForm").classList.toggle("hidden", state.user.role !== "Admin");
}

function renderFlowers() {
    const body = $("flowersBody");
    body.innerHTML = "";
    state.flowers.forEach((flower) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${escapeHtml(flower.name)}</td>
            <td>${escapeHtml(flower.color)}</td>
            <td>${Number(flower.price).toFixed(2)}</td>
            <td></td>
            <td></td>
        `;

        const stockCell = tr.children[3];
        if (["Admin", "Florist"].includes(state.user.role)) {
            const wrapper = document.createElement("div");
            wrapper.className = "stock-control";
            wrapper.innerHTML = `
                <input type="number" min="0" step="1" value="${flower.stock}" aria-label="${t("stock")}">
                <button type="button">${t("update")}</button>
            `;
            wrapper.querySelector("button").addEventListener("click", () => updateStock(flower.id, wrapper.querySelector("input").value));
            stockCell.appendChild(wrapper);
        } else {
            stockCell.textContent = flower.stock;
        }

        const actionsCell = tr.children[4];
        if (state.user.role === "Admin") {
            const actions = document.createElement("div");
            actions.className = "row-actions";
            actions.innerHTML = `
                <button type="button" class="secondary">${t("edit")}</button>
                <button type="button" class="danger">${t("delete")}</button>
            `;
            actions.children[0].addEventListener("click", () => fillFlowerForm(flower));
            actions.children[1].addEventListener("click", () => deleteFlower(flower.id));
            actionsCell.appendChild(actions);
        } else if (state.user.role === "Florist") {
            actionsCell.textContent = t("stockOnly");
        } else {
            actionsCell.textContent = t("noActions");
        }
        body.appendChild(tr);
    });
}

function fillFlowerForm(flower) {
    ensureColorOption(flower.color);
    $("flowerId").value = flower.id;
    $("flowerName").value = flower.name;
    $("flowerColor").value = flower.color;
    $("flowerPrice").value = flower.price;
    $("flowerStock").value = flower.stock;
}

function resetFlowerForm() {
    $("flowerForm").reset();
    $("flowerId").value = "";
    $("flowerColor").value = colorOptions[0];
}

function ensureColorOption(color) {
    if (!color || colorOptions.includes(color)) return;
    colorOptions.push(color);
    populateColorSelects();
}

async function loadSession() {
    try {
        const data = await api("/api/session");
        state.user = data.user;
        state.hasEntered = data.entered || data.authenticated;
        renderUser();
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function loadFlowers() {
    try {
        const params = new URLSearchParams();
        if ($("colorFilter").value.trim()) params.set("color", $("colorFilter").value.trim());
        if ($("sortSelect").value) params.set("sort", $("sortSelect").value);
        const data = await api(`/api/flowers?${params.toString()}`);
        state.flowers = data.flowers;
        renderFlowers();
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function login(event) {
    event.preventDefault();
    try {
        const data = await api("/api/login", {
            method: "POST",
            body: JSON.stringify({ email: $("email").value, password: $("password").value })
        });
        state.user = data.user;
        state.hasEntered = true;
        renderUser();
        connectChat();
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function browseAsVisitor() {
    try {
        const data = await api("/api/visitor", { method: "POST", body: "{}" });
        state.user = data.user;
        state.hasEntered = true;
        renderUser();
        connectChat();
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function logout() {
    try {
        await api("/api/logout", { method: "POST", body: "{}" });
        state.user = { name: "Visitor", email: "guest@flowershop.com", role: "Visitor" };
        state.hasEntered = false;
        renderUser();
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function saveFlower(event) {
    event.preventDefault();
    const id = $("flowerId").value;
    const payload = {
        name: $("flowerName").value,
        color: $("flowerColor").value,
        price: $("flowerPrice").value,
        stock: $("flowerStock").value
    };
    try {
        await api(id ? `/api/flowers/${id}` : "/api/flowers", {
            method: id ? "PUT" : "POST",
            body: JSON.stringify(payload)
        });
        resetFlowerForm();
        await loadFlowers();
        showMessage(t("saved"));
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function updateStock(id, stock) {
    try {
        await api(`/api/flowers/${id}/stock`, {
            method: "PATCH",
            body: JSON.stringify({ stock })
        });
        await loadFlowers();
        showMessage(t("stockUpdated"));
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function deleteFlower(id) {
    try {
        await api(`/api/flowers/${id}`, { method: "DELETE" });
        await loadFlowers();
        showMessage(t("deleted"));
    } catch (error) {
        showMessage(error.message, true);
    }
}

function connectChat() {
    if (state.socket || typeof io !== "function") {
        if (typeof io !== "function") showMessage(t("chatUnavailable"), true);
        return;
    }
    state.socket = io({ transports: ["websocket", "polling"] });
    state.socket.on("chat_message", appendChatMessage);
}

function sendChat(event) {
    event.preventDefault();
    const input = $("chatInput");
    const text = input.value.trim();
    if (!text) return;
    if (!state.socket) connectChat();
    if (state.socket) {
        state.socket.emit("chat_message", { sender: state.user.name || state.user.email || t("visitor"), text });
        input.value = "";
    }
}

function appendChatMessage(message) {
    const row = document.createElement("div");
    row.className = "chat-message";
    row.innerHTML = `
        <div class="chat-meta">${escapeHtml(message.sender)} - ${escapeHtml(message.timestamp)}</div>
        <div>${escapeHtml(message.text)}</div>
    `;
    $("chatMessages").appendChild(row);
    $("chatMessages").scrollTop = $("chatMessages").scrollHeight;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function bindEvents() {
    $("languageSelect").addEventListener("change", (event) => {
        state.language = event.target.value;
        localStorage.setItem("language", state.language);
        applyTranslations();
    });
    $("loginForm").addEventListener("submit", login);
    $("visitorBtn").addEventListener("click", browseAsVisitor);
    $("logoutBtn").addEventListener("click", logout);
    $("applyFiltersBtn").addEventListener("click", loadFlowers);
    $("flowerForm").addEventListener("submit", saveFlower);
    $("cancelEditBtn").addEventListener("click", resetFlowerForm);
    $("chatForm").addEventListener("submit", sendChat);
    $("chatToggle").addEventListener("click", () => {
        $("chatPanel").classList.toggle("hidden");
        connectChat();
        if (!$("chatPanel").classList.contains("hidden")) {
            $("chatInput").focus();
        }
    });
    $("chatClose").addEventListener("click", () => $("chatPanel").classList.add("hidden"));
}

bindEvents();
populateColorSelects();
applyTranslations();
loadSession().then(loadFlowers);
