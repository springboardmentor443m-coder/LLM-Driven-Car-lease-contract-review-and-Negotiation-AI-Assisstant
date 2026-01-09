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

// ---------------- PROS & CONS (UPDATED PHASE 6) ----------------
async function getFairness() {
  if (!CONTRACT_ID) return alert("Upload contract first");

  const res = await fetch(`${API}/${CONTRACT_ID}/fairness`);
  const data = await res.json();

  if (!res.ok) {
    document.getElementById("fairnessResult").innerHTML =
      `<code style="color:red">${data.detail || "Analysis failed"}</code>`;
    return;
  }

  let output = "";

  output += "✅ PROS:\n";
  if (data.pros.length === 0) {
    output += "- No strong advantages detected\n";
  } else {
    data.pros.forEach(p => output += `- ${p}\n`);
  }

  output += "\n⚠️ CONS:\n";
  if (data.cons.length === 0) {
    output += "- No major issues detected\n";
  } else {
    data.cons.forEach(c => output += `- ${c}\n`);
  }

  output += "\n💡 NEGOTIATION OPPORTUNITIES:\n";
  if (data.negotiation_opportunities.length === 0) {
    output += "- No clear negotiation points\n";
  } else {
    data.negotiation_opportunities.forEach(n => output += `- ${n}\n`);
  }

  output += `\n📝 SUMMARY:\n${data.summary}`;

  document.getElementById("fairnessResult").innerHTML =
    `<code>${output}</code>`;
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
