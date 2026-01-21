import { useState } from "react";
import api from "../api/client";

function Negotiation({ batchId, valuations }) {
  const [question, setQuestion] = useState("");
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(null);

  const askAi = async (filename) => {
    if (!question.trim()) {
      alert("Please enter a question");
      return;
    }

    try {
      setLoading(filename);

      const res = await api.post("/api/negotiate/negotiate", {
        batch_id: batchId,
        filename: filename,
        question: question
      });

      setAnswers((prev) => ({
        ...prev,
        [filename]: res.data.answer
      }));
    } catch (err) {
      console.error(err);
      alert("Negotiation AI failed");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div style={{ marginTop: "30px" }}>
      <h2>🤖 AI Negotiator</h2>

      <textarea
        rows={3}
        style={{ width: "100%", marginBottom: "10px" }}
        placeholder="Ask anything... (pricing, negotiation, clauses, email draft)"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      {Object.entries(valuations).map(([filename, v]) => (
        <div
          key={filename}
          style={{
            border: "1px solid #ccc",
            padding: "10px",
            marginBottom: "12px"
          }}
        >
          <strong>{filename}</strong>
          <p>
            Fair Monthly Lease: $
            {v.fair_lease_pricing.fair_monthly_lease}
          </p>

          <button onClick={() => askAi(filename)}>
            {loading === filename ? "Thinking..." : "Ask AI"}
          </button>

          {answers[filename] && (
            <div style={{ marginTop: "10px", background: "#f9f9f9", padding: "10px" }}>
              <b>AI Advice:</b>
              <p>{answers[filename]}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default Negotiation;
