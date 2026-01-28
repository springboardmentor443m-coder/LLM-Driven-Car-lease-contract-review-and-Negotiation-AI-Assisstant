import React, { useState } from "react";

function Dashboard({ contractText, slaData, setSlaData }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const extractSLA = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:5000/api/extract-sla", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          contract_text: contractText
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSlaData(data.sla_summary);
      } else {
        setError(data.error || "Failed to extract SLA");
      }
    } catch (err) {
      setError("Backend server not reachable");
    }

    setLoading(false);
  };

  return (
    <div style={{ border: "1px solid #aaa", padding: "15px", marginBottom: "20px" }}>
      <h2>SLA Extraction Dashboard</h2>

      <button onClick={extractSLA} disabled={loading}>
        {loading ? "Extracting..." : "Extract SLA"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {slaData && (
        <div style={{ marginTop: "15px" }}>
          <h3>Extracted Contract Summary</h3>

          <pre
            style={{
              background: "#f4f4f4",
              padding: "10px",
              overflowX: "auto"
            }}
          >
            {typeof slaData === "string"
              ? slaData
              : JSON.stringify(slaData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
