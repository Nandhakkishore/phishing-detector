const API_BASE = "https://phishing-detector-a3ek.onrender.com";
const targetEl = document.getElementById("target");
const panelEl = document.getElementById("statusPanel");
const statusEl = document.getElementById("status");
const confLabelEl = document.getElementById("confidenceLabel");
const confFillEl = document.getElementById("confidenceBarFill");
const reasonsEl = document.getElementById("reasons");
const scanBtn = document.getElementById("scanBtn");
const reportBtn = document.getElementById("reportBtn");

let currentUrl = null;
let currentClassification = null;

function setPanelState(cls) {
  panelEl.className = cls;
  statusEl.className = cls;
  confFillEl.className = cls;
}

function setStatus(classification, confidence) {
  setPanelState(classification);
  statusEl.textContent = classification;
  confLabelEl.textContent = `${(confidence * 100).toFixed(1)}%`;
  confFillEl.style.width = `${(confidence * 100).toFixed(1)}%`;
}

function setReasons(reasons) {
  reasonsEl.innerHTML = "";
  reasons.forEach((r) => {
    const li = document.createElement("li");
    li.textContent = r;
    reasonsEl.appendChild(li);
  });
}

async function scanUrl(url) {
  targetEl.textContent = url;
  setPanelState("loading");
  statusEl.textContent = "Scanning";
  confLabelEl.textContent = "—";
  confFillEl.style.width = "0%";
  reasonsEl.innerHTML = "";

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await response.json();

    currentUrl = url;
    currentClassification = data.classification;

    setStatus(data.classification, data.confidence);
    setReasons(data.reasons);
  } catch (err) {
    setPanelState("phishing");
    statusEl.textContent = "Error";
    reasonsEl.innerHTML = `<li>Could not reach detection API: ${err.message}</li>`;
  }
}

function getActiveTabUrl(callback) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0] && tabs[0].url) callback(tabs[0].url);
  });
}

getActiveTabUrl((url) => scanUrl(url));

scanBtn.addEventListener("click", () => {
  getActiveTabUrl((url) => scanUrl(url));
});

reportBtn.addEventListener("click", async () => {
  if (!currentUrl || !currentClassification) return;
  try {
    await fetch(`${API_BASE}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: currentUrl,
        original_classification: currentClassification,
        user_comment: "Reported as incorrect via extension",
      }),
    });
    reportBtn.textContent = "Reported ✓";
    reportBtn.disabled = true;
  } catch (err) {
    reportBtn.textContent = "Report failed";
  }
});