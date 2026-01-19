// FILE UPLOAD LOGIC
const fileInput = document.getElementById("fileInput");
if (fileInput) fileInput.onchange = analyzePDF;

async function analyzePDF() {
    const file = fileInput.files[0];
    if (!file) return;

    document.getElementById("loadingOverlay").style.display = "flex";

    const form = new FormData();
    form.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: form
    });

    const data = await res.json();
    localStorage.setItem("analysis", JSON.stringify(data));
    window.location = "dashboard.html";
}

// DASHBOARD LOAD
const saved = localStorage.getItem("analysis");
if (saved && window.location.pathname.includes("dashboard")) {
    const data = JSON.parse(saved);

    renderSummary(data.summary);
    renderFairness(data.fairness_score, data.fairness_reasons);
    renderTips(data.negotiation_tips);
    renderVIN(data.vin_info);

    setupSidebar();
    setupChat(data);
}

// SUMMARY SECTIONs
function renderSummary(raw) {
    let txt = raw.replace(/\*\*/g, "");

    // Clean newline spacing
    txt = txt.replace(/\n{2,}/g, "\n");
    txt = txt.replace(/\n/g, "<br>");

    // Convert section markers to header tags
    txt = txt.replace(/Lease Contract Summary:/, `<h3>Lease Contract Summary:</h3>`);
    txt = txt.replace(/Risks:/, `<h3>Risks:</h3>`);
    txt = txt.replace(/Negotiation Advice:/, `<h3>Negotiation Advice:</h3>`);

    document.getElementById("summary").innerHTML = `
        <div class="section-title">Document Summary</div>
        <div class="card summary">${txt}</div>
    `;
}

function renderFairness(score, reasons) {
    document.getElementById("fairness").innerHTML = `
    <div class="section">
        <div class="section-title">Fairness Score</div>
        <div class="card summary-card">
            <p><b>Score:</b> ${score}/100</p>
            ${reasons.map(r=>`<p>${r}</p>`).join("")}
        </div>
    </div>`;
}



// FAIRNESS


// TIPS
function renderTips(tips) {
    const html = `
    <div class="section-title">Negotiation Tips</div>
    ${tips.map(t=>`<div class="card">${t}</div>`).join("")}`;
    document.getElementById("tips").innerHTML = html;
}

// VIN
function renderVIN(vin) {
    const html = `
    <div class="section-title">VIN Information</div>
    <div class="card"><b>Valid:</b> ${vin.valid ? "Yes" : "No"}</div><br>
    ${vin.valid ? `
    <div class="card">
        ${Object.entries(vin.vehicle).map(([k,v])=>`<p><b>${k}:</b> ${v}</p>`).join("")}
    </div>` : ""}`;
    document.getElementById("vin").innerHTML = html;
}

// SIDEBAR TAB SWITCHING
function setupSidebar() {
    document.querySelectorAll(".nav-item").forEach(item => {
        item.onclick = () => {
            document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
            item.classList.add("active");

            document.querySelectorAll(".main > div").forEach(s => s.style.display = "none");
            document.getElementById(item.dataset.section).style.display = "block";
        }
    });
}

// CHAT AI
function setupChat(data) {
    const btn = document.getElementById("chatSend");
    btn.onclick = async () => {
        const q = document.getElementById("chatInput").value;
        const box = document.getElementById("chatBox");
        if (!q) return;

        box.innerHTML += `<div><b>You:</b> ${q}</div>`;

        const res = await fetch("http://127.0.0.1:8000/chat", {
            method:"POST",
            headers:{ "Content-Type":"application/json" },
            body: JSON.stringify({ question:q, data })
        });

        const reply = await res.json();
        box.innerHTML += `<div><b>AI:</b> ${reply.answer || "Not specified in the contract"}</div>`;
        box.scrollTop = box.scrollHeight;
    };
}
