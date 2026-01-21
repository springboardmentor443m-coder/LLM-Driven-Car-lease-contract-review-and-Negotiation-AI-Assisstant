import { useState } from "react";
import api from "../api/client";

function Valuation({ batchId, contracts, setValuations }) {
  const [loading, setLoading] = useState(null);

  const runValuation = async (filename) => {
    try {
      setLoading(filename);
      const res = await api.get(
        `/api/valuation/${batchId}/${filename}`
      );

      // save valuation result
      setValuations((prev) => ({
        ...prev,
        [filename]: res.data,
      }));

      alert(`Valuation completed for ${filename}`);
    } catch (err) {
      console.error(err);
      alert("Valuation failed");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div>
      <h2>3️⃣ Valuation</h2>

      {contracts.map((c) => (
        <div key={c.contract_id} style={{ marginBottom: "10px" }}>
          <span>{c.filename}</span>

          <button
            style={{ marginLeft: "10px" }}
            onClick={() => runValuation(c.filename)}
            disabled={loading === c.filename}
          >
            {loading === c.filename ? "Running..." : "Run Valuation"}
          </button>
        </div>
      ))}
    </div>
  );
}

export default Valuation;
