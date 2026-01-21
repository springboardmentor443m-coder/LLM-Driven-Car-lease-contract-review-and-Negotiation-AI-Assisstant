import { useState } from "react";
import Upload from "./components/Upload";
import Ocr from "./components/Ocr";
import Valuation from "./components/Valuation";
import Negotiation from "./components/Negotiation";


function App() {
  const [batchId, setBatchId] = useState(null);
  const [contracts, setContracts] = useState([]);
  const [valuations, setValuations] = useState({});

  return (
    <div style={{ padding: "20px" }}>
      <h1>🚗 Car Lease AI Assistant</h1>

      {/* DEBUG */}
      <div style={{ background: "#eee", padding: "10px", marginBottom: "20px" }}>
        <b>DEBUG STATE</b>
        <pre>{JSON.stringify({ batchId, contracts, valuations }, null, 2)}</pre>
      </div>

      <Upload setBatchId={setBatchId} setContracts={setContracts} />

      {batchId && contracts.length > 0 && (
        <Ocr batchId={batchId} contracts={contracts} />
      )}

      {batchId && contracts.length > 0 && (
        <Valuation
          batchId={batchId}
          contracts={contracts}
          setValuations={setValuations}
        />
      )}

      {Object.keys(valuations).length > 0 && (
        <div>
          <h2>📊 Valuation Results</h2>

          {Object.entries(valuations).map(([filename, v]) => (
            <div key={filename} style={{ marginBottom: "12px" }}>
              <strong>{filename}</strong>
              <ul>
                <li>MSRP: ${v.msrp}</li>
                <li>Residual Value: ${v.residual_value.final_value}</li>
                <li>
                  Fair Monthly Lease: $
                  {v.fair_lease_pricing.fair_monthly_lease}
                </li>
              </ul>
            </div>
          ))}
        </div>
      )}
      {Object.keys(valuations).length > 0 && (
  <Negotiation
    batchId={batchId}
    valuations={valuations}
  />
)}

    </div>
  );
}

export default App;
