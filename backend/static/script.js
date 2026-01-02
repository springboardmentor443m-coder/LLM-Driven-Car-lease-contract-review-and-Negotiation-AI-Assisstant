const API = "/contracts";
let CONTRACT_ID = null;

// ---------------- Upload ----------------
async function uploadContract() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return alert("Select a file");

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API}/upload`, {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  CONTRACT_ID = data.id;

  document.getElementById("contractIdText").innerHTML =
    `✅ Contract uploaded. ID: <b>${CONTRACT_ID}</b>`;
}

// ---------------- SLA ----------------
async function extractSLA() {
  if (!CONTRACT_ID) return alert("Upload contract first");

  const res = await fetch(`${API}/${CONTRACT_ID}/extract-sla`, {
    method: "POST"
  });

  const data = await res.json();
  document.getElementById("slaResult").innerHTML =
    `<code>${JSON.stringify(data.sla, null, 2)}</code>`;
}

// ---------------- Vehicle ----------------
async function getVehicle() {
  if (!CONTRACT_ID) return alert("Upload contract first");

  const res = await fetch(`${API}/${CONTRACT_ID}/vehicle-info`);
  const data = await res.json();

  document.getElementById("vehicleResult").innerHTML =
    `<code>${JSON.stringify(data, null, 2)}</code>`;
}

// ---------------- Fairness ----------------
async function getFairness() {
  if (!CONTRACT_ID) return alert("Upload contract first");

  const res = await fetch(`${API}/${CONTRACT_ID}/fairness-score`);
  const data = await res.json();

  document.getElementById("fairnessScore").innerText = data.fairness_score;
  document.getElementById("riskLevel").innerText = data.risk_level;

  document.getElementById("fairnessResult").innerHTML =
    `<code>${JSON.stringify(data, null, 2)}</code>`;

  document.getElementById("fairnessMetrics").style.display = "flex";
  document.getElementById("fairnessMetrics").style.opacity = 1;
}

// ---------------- Chatbot ----------------
async function chat() {
  if (!CONTRACT_ID) return alert("Upload contract first");

  const question = document.getElementById("chatInput").value;
  if (!question) return;

  const res = await fetch(
    `${API}/${CONTRACT_ID}/chat?question=${encodeURIComponent(question)}`,
    { method: "POST" }
  );

  const data = await res.json();
  document.getElementById("chatResult").innerHTML =
    `<code>${data.answer}</code>`;
}

// ---------------- Report ----------------
function downloadReport() {
  if (!CONTRACT_ID) return alert("Upload contract first");
  window.open(`${API}/${CONTRACT_ID}/report/pdf`, "_blank");
}
