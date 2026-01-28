import React, { useState } from "react";

function Upload({ setContractText }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/upload", {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setContractText(data.extracted_text);
        setMessage("File uploaded and text extracted successfully");
      } else {
        setMessage(data.error || "Upload failed");
      }
    } catch (error) {
      setMessage("Backend server not running");
    }

    setLoading(false);
  };

  return (
    <div style={{ border: "1px solid #ccc", padding: "15px", marginBottom: "20px" }}>
      <h2>Upload Lease / Loan Contract</h2>

      <input type="file" onChange={handleFileChange} />

      <br /><br />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {message && <p>{message}</p>}
    </div>
  );
}

export default Upload;
