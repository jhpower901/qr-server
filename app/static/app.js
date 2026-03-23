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

function updateTypeUI() {
  const type = getValue("type");

  setHidden("section-wifi", type !== "wifi");
  setHidden("section-text-url", type === "wifi");

  setHidden("row-data", type === "url");
  setHidden("row-url", type !== "url");
}

function collectPayload() {
  const type = getValue("type");

  const payload = {
    type,
    style: getValue("style"),
    format: getValue("format"),
    scale: parseInt(getValue("scale"), 10),
    border: parseInt(getValue("border"), 10),
    error_correction: getValue("error_correction"),
    optimize: parseInt(getValue("optimize"), 10),
    jpg_quality: parseInt(getValue("jpg_quality"), 10),
    fg_r: parseInt(getValue("fg_r"), 10),
    fg_g: parseInt(getValue("fg_g"), 10),
    fg_b: parseInt(getValue("fg_b"), 10),
    bg_r: parseInt(getValue("bg_r"), 10),
    bg_g: parseInt(getValue("bg_g"), 10),
    bg_b: parseInt(getValue("bg_b"), 10),
  };

  const versionRaw = getValue("version").trim();
  if (versionRaw !== "") {
    payload.version = parseInt(versionRaw, 10);
  }

  if (type === "text") {
    payload.data = getValue("data");
  } else if (type === "url") {
    payload.url = getValue("url");
  } else if (type === "wifi") {
    payload.ssid = getValue("ssid");
    payload.password = getValue("password");
    payload.encryption = getValue("encryption");
    payload.hidden = $("hidden").checked;
  }

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
  }, 250);
}

function updateFormatHint() {
  const format = getValue("format");
  const hint = $("hint");

  if (format === "png") {
    hint.textContent = "PNG는 배경이 투명합니다.";
  } else if (format === "jpg") {
    hint.textContent = "JPG는 배경색이 적용됩니다.";
  } else {
    hint.textContent = "SVG는 벡터 포맷이며 배경색이 적용됩니다.";
  }
}

async function renderQr(download = false) {
  showError("");

  const payload = collectPayload();
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

  const blob = await response.blob();
  return blob;
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
    const payload = collectPayload();
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

async function copyImageUrl() {
  try {
    const payload = collectPayload();
    const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(payload))))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/g, "");

    const url = `${window.location.origin}/ui?payload=${encoded}`;
    await navigator.clipboard.writeText(url);
    $("hint").textContent = "공유용 UI 링크를 클립보드에 복사했습니다.";
  } catch (err) {
    showError("링크 복사에 실패했습니다.");
  }
}

function applyPayloadFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const payload = params.get("payload");
  if (!payload) return;

  try {
    const padded = payload + "=".repeat((4 - payload.length % 4) % 4);
    const json = decodeURIComponent(escape(atob(padded.replace(/-/g, "+").replace(/_/g, "/"))));
    const data = JSON.parse(json);

    if (data.type) $("type").value = data.type;
    updateTypeUI();

    if (data.style) $("style").value = data.style;
    if (data.format) $("format").value = data.format;
    if (data.scale != null) $("scale").value = data.scale;
    if (data.border != null) $("border").value = data.border;
    if (data.error_correction) $("error_correction").value = data.error_correction;
    if (data.optimize != null) $("optimize").value = data.optimize;
    if (data.jpg_quality != null) $("jpg_quality").value = data.jpg_quality;
    if (data.version != null) $("version").value = data.version;

    if (data.fg_r != null) $("fg_r").value = data.fg_r;
    if (data.fg_g != null) $("fg_g").value = data.fg_g;
    if (data.fg_b != null) $("fg_b").value = data.fg_b;

    if (data.bg_r != null) $("bg_r").value = data.bg_r;
    if (data.bg_g != null) $("bg_g").value = data.bg_g;
    if (data.bg_b != null) $("bg_b").value = data.bg_b;

    if (data.type === "text" && data.data != null) $("data").value = data.data;
    if (data.type === "url" && data.url != null) $("url").value = data.url;

    if (data.type === "wifi") {
      if (data.ssid != null) $("ssid").value = data.ssid;
      if (data.password != null) $("password").value = data.password;
      if (data.encryption != null) $("encryption").value = data.encryption;
      $("hidden").checked = !!data.hidden;
    }
  } catch (_) {}
}

window.addEventListener("DOMContentLoaded", () => {
  $("type").addEventListener("change", () => {
    updateTypeUI();
    debouncePreview();
  });

  $("btn-preview").addEventListener("click", previewQr);
  $("btn-download").addEventListener("click", downloadQr);
  $("btn-copy").addEventListener("click", copyImageUrl);

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

  updateTypeUI();
  applyPayloadFromQuery();
  updateFormatHint();
  previewQr();
});