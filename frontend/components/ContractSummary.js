import React from "react";

function ContractSummary({ slaData }) {
  if (!slaData) {
    return null;
  }

  // If SLA comes as string (from LLM)
  if (typeof slaData === "string") {
    return (
      <div style={{ marginTop: "15px" }}>
        <h3>Contract Summary</h3>
        <pre
          style={{
            background: "#f4f4f4",
            padding: "10px",
            whiteSpace: "pre-wrap"
          }}
        >
          {slaData}
        </pre>
      </div>
    );
  }

  // If SLA comes as JSON
  return (
    <div style={{ marginTop: "15px" }}>
      <h3>Contract Summary</h3>

      <table
        border="1"
        cellPadding="8"
        style={{ borderCollapse: "collapse", width: "100%" }}
      >
        <tbody>
          {Object.entries(slaData).map(([key, value]) => (
            <tr key={key}>
              <td><strong>{key}</strong></td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ContractSummary;
