import React, { useState } from "react";
import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";
import VinLookup from "./pages/VinLookup";

function App() {
  const [contractText, setContractText] = useState("");
  const [slaData, setSlaData] = useState(null);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Car Lease Contract Review & Negotiation AI</h1>

      {/* Contract Upload */}
      <Upload setContractText={setContractText} />

      {/* SLA Dashboard */}
      {contractText && (
        <Dashboard
          contractText={contractText}
          slaData={slaData}
          setSlaData={setSlaData}
        />
      )}

      {/* VIN Lookup */}
      <VinLookup />
    </div>
  );
}

export default App;
