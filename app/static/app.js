function $(id) {
  return document.getElementById(id);
}

function getValue(id) {
  return $(id).value;
}

function setHidden(id, hidden) {
  $(id).classList.toggle("hidden", hidden);
}

function showError(message) {
  const el = $("error");
  if (!message) {
    el.textContent = "";
    el.classList.add("hidden");
    return;
  }
  el.textContent = message;
  el.classList.remove("hidden");
}

function updateTypePanels() {
  const type = getValue("qr_type");

  const panels = [
    "panel-text",
    "panel-url",
    "panel-wifi",
    "panel-email",
    "panel-phone",
    "panel-sms",
    "panel-vcard",
  ];

  for (const panelId of panels) {
    setHidden(panelId, true);
  }

  const activePanel = {
    text: "panel-text",
    url: "panel-url",
    wifi: "panel-wifi",
    email: "panel-email",
    phone: "panel-phone",
    sms: "panel-sms",
    vcard: "panel-vcard",
  }[type];

  if (activePanel) {
    setHidden(activePanel, false);
  }
}

function updateFormatHint() {
  const format = getValue("format");
  const hint = $("hint");

  if (format === "png") {
    hint.textContent = "PNG는 배경이 투명합니다.";
  } else if (format === "jpg" || format === "jpeg") {
    hint.textContent = "JPG는 배경색이 적용됩니다.";
  } else {
    hint.textContent = "SVG는 벡터 포맷이며 배경색이 적용됩니다.";
  }
}

function parseNumber(id, fallback = 0) {
  const value = parseInt(getValue(id), 10);
  return Number.isNaN(value) ? fallback : value;
}

function buildUiState() {
  return {
    type: getValue("qr_type"),

    text: getValue("text_value"),
    text_b64: getValue("text_b64"),

    url: getValue("url_value"),
    url_b64: getValue("url_b64"),

    wifi_ssid: getValue("wifi_ssid"),
    wifi_password: getValue("wifi_password"),
    wifi_encryption: getValue("wifi_encryption"),
    wifi_hidden: $("wifi_hidden").checked,

    email_address: getValue("email_address"),
    email_subject: getValue("email_subject"),
    email_body: getValue("email_body"),

    phone_number: getValue("phone_number"),

    sms_number: getValue("sms_number"),
    sms_message: getValue("sms_message"),

    vcard_name: getValue("vcard_name"),
    vcard_phone: getValue("vcard_phone"),
    vcard_email: getValue("vcard_email"),

    style: getValue("style"),
    format: getValue("format"),
    error_correction: getValue("error_correction"),

    scale: parseNumber("scale", 10),
    border: parseNumber("border", 4),
    optimize: parseNumber("optimize", 20),
    jpg_quality: parseNumber("jpg_quality", 95),

    version: getValue("version").trim(),

    fg_r: parseNumber("fg_r", 0),
    fg_g: parseNumber("fg_g", 0),
    fg_b: parseNumber("fg_b", 0),

    bg_r: parseNumber("bg_r", 255),
    bg_g: parseNumber("bg_g", 255),
    bg_b: parseNumber("bg_b", 255),
  };
}

function buildApiPayload() {
  const state = buildUiState();
  const payload = { ...state };

  if (payload.version === "") {
    delete payload.version;
  } else {
    payload.version = parseInt(payload.version, 10);
  }

  if (!payload.text) delete payload.text;
  if (!payload.text_b64) delete payload.text_b64;
  if (!payload.url) delete payload.url;
  if (!payload.url_b64) delete payload.url_b64;

  if (!payload.wifi_ssid) delete payload.wifi_ssid;
  if (!payload.wifi_password) delete payload.wifi_password;

  if (!payload.email_address) delete payload.email_address;
  if (!payload.email_subject) delete payload.email_subject;
  if (!payload.email_body) delete payload.email_body;

  if (!payload.phone_number) delete payload.phone_number;

  if (!payload.sms_number) delete payload.sms_number;
  if (!payload.sms_message) delete payload.sms_message;

  if (!payload.vcard_name) delete payload.vcard_name;
  if (!payload.vcard_phone) delete payload.vcard_phone;
  if (!payload.vcard_email) delete payload.vcard_email;

  return payload;
}

let previewObjectUrl = null;
let previewTimer = null;

function revokePreviewUrl() {
  if (previewObjectUrl) {
    URL.revokeObjectURL(previewObjectUrl);
    previewObjectUrl = null;
  }
}

function debouncePreview() {
  clearTimeout(previewTimer);
  previewTimer = setTimeout(() => {
    previewQr();
  }, 220);
}

async function renderQr(download = false) {
  showError("");

  const payload = buildApiPayload();
  payload.download = download;

  const response = await fetch("/render", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      if (data && data.detail) {
        message = data.detail;
      }
    } catch (_) {}
    throw new Error(message);
  }

  return await response.blob();
}

async function previewQr() {
  try {
    const blob = await renderQr(false);
    revokePreviewUrl();
    previewObjectUrl = URL.createObjectURL(blob);
    $("preview").src = previewObjectUrl;
    updateFormatHint();
  } catch (err) {
    showError(String(err.message || err));
  }
}

async function downloadQr() {
  try {
    const blob = await renderQr(true);
    const payload = buildApiPayload();

    const format = payload.format || "png";
    const type = payload.type || "qr";
    const ext = format === "jpeg" ? "jpg" : format;
    const filename = `${type}-qr.${ext}`;

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    showError(String(err.message || err));
  }
}

function serializeUiStateForShare(state) {
  const json = JSON.stringify(state);
  return btoa(unescape(encodeURIComponent(json)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function parseSharedUiState(encoded) {
  const padded = encoded + "=".repeat((4 - encoded.length % 4) % 4);
  const json = decodeURIComponent(
    escape(atob(padded.replace(/-/g, "+").replace(/_/g, "/")))
  );
  return JSON.parse(json);
}

async function copyShareLink() {
  try {
    const state = buildUiState();
    const encoded = serializeUiStateForShare(state);
    const url = `${window.location.origin}/ui?payload=${encoded}`;
    await navigator.clipboard.writeText(url);
    $("hint").textContent = "현재 UI 상태를 담은 공유 링크를 복사했습니다.";
  } catch (err) {
    showError("공유 링크 복사에 실패했습니다.");
  }
}

function applyUiState(state) {
  if (state.type != null) $("qr_type").value = state.type;

  if (state.text != null) $("text_value").value = state.text;
  if (state.text_b64 != null) $("text_b64").value = state.text_b64;

  if (state.url != null) $("url_value").value = state.url;
  if (state.url_b64 != null) $("url_b64").value = state.url_b64;

  if (state.wifi_ssid != null) $("wifi_ssid").value = state.wifi_ssid;
  if (state.wifi_password != null) $("wifi_password").value = state.wifi_password;
  if (state.wifi_encryption != null) $("wifi_encryption").value = state.wifi_encryption;
  if (state.wifi_hidden != null) $("wifi_hidden").checked = !!state.wifi_hidden;

  if (state.email_address != null) $("email_address").value = state.email_address;
  if (state.email_subject != null) $("email_subject").value = state.email_subject;
  if (state.email_body != null) $("email_body").value = state.email_body;

  if (state.phone_number != null) $("phone_number").value = state.phone_number;

  if (state.sms_number != null) $("sms_number").value = state.sms_number;
  if (state.sms_message != null) $("sms_message").value = state.sms_message;

  if (state.vcard_name != null) $("vcard_name").value = state.vcard_name;
  if (state.vcard_phone != null) $("vcard_phone").value = state.vcard_phone;
  if (state.vcard_email != null) $("vcard_email").value = state.vcard_email;

  if (state.style != null) $("style").value = state.style;
  if (state.format != null) $("format").value = state.format;
  if (state.error_correction != null) $("error_correction").value = state.error_correction;

  if (state.scale != null) $("scale").value = state.scale;
  if (state.border != null) $("border").value = state.border;
  if (state.optimize != null) $("optimize").value = state.optimize;
  if (state.jpg_quality != null) $("jpg_quality").value = state.jpg_quality;
  if (state.version != null) $("version").value = state.version;

  if (state.fg_r != null) $("fg_r").value = state.fg_r;
  if (state.fg_g != null) $("fg_g").value = state.fg_g;
  if (state.fg_b != null) $("fg_b").value = state.fg_b;

  if (state.bg_r != null) $("bg_r").value = state.bg_r;
  if (state.bg_g != null) $("bg_g").value = state.bg_g;
  if (state.bg_b != null) $("bg_b").value = state.bg_b;

  updateTypePanels();
}

function applyPayloadFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const payload = params.get("payload");
  if (!payload) return;

  try {
    const state = parseSharedUiState(payload);
    applyUiState(state);
  } catch (_) {
    showError("공유 링크 payload를 읽지 못했습니다.");
  }
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function bindStepper(button) {
  button.addEventListener("click", () => {
    const targetId = button.dataset.target;
    const delta = parseInt(button.dataset.delta, 10);

    const input = $(targetId);
    const min = input.min !== "" ? parseInt(input.min, 10) : Number.MIN_SAFE_INTEGER;
    const max = input.max !== "" ? parseInt(input.max, 10) : Number.MAX_SAFE_INTEGER;
    const current = parseNumber(targetId, 0);
    const next = clamp(current + delta, min, max);

    input.value = next;
    debouncePreview();
  });
}

window.addEventListener("DOMContentLoaded", () => {
  $("qr_type").addEventListener("change", () => {
    updateTypePanels();
    debouncePreview();
  });

  $("format").addEventListener("change", updateFormatHint);

  $("btn-preview").addEventListener("click", previewQr);
  $("btn-download").addEventListener("click", downloadQr);
  $("btn-copy").addEventListener("click", copyShareLink);

  document.querySelectorAll("input, select, textarea").forEach((el) => {
    el.addEventListener("input", debouncePreview);
    el.addEventListener("change", debouncePreview);
  });

  document.querySelectorAll(".preset-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const [fr, fg, fb] = btn.dataset.fg.split(",").map(Number);
      const [br, bg, bb] = btn.dataset.bg.split(",").map(Number);

      $("fg_r").value = fr;
      $("fg_g").value = fg;
      $("fg_b").value = fb;

      $("bg_r").value = br;
      $("bg_g").value = bg;
      $("bg_b").value = bb;

      debouncePreview();
    });
  });

  document.querySelectorAll(".spin-btn").forEach(bindStepper);

  updateTypePanels();
  applyPayloadFromQuery();
  updateFormatHint();
  previewQr();
});
