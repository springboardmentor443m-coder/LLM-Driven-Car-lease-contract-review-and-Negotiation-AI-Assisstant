import api from "../api/client";

function Ocr({ batchId, contracts }) {
  if (!batchId || !contracts?.length) return null;

  const runOcr = async (filename) => {
    try {
      await api.get(`/api/ocr/ocr/${batchId}/${filename}`);
      alert(`OCR completed for ${filename}`);
    } catch (err) {
      console.error(err);
      alert("OCR failed");
    }
  };

  return (
    <div>
      <h2>2️⃣ OCR</h2>

      {contracts.map((c) => (
        <div key={c.contract_id} style={{ marginBottom: "8px" }}>
          <span>{c.filename}</span>
          <button
            style={{ marginLeft: "10px" }}
            onClick={() => runOcr(c.filename)}
          >
            Run OCR
          </button>
        </div>
      ))}
    </div>
  );
}

export default Ocr;
