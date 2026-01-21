import { useState } from "react";
import api from "../api/client";

function Upload({ setBatchId, setContracts }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) {
      alert("Please select files first");
      return;
    }

    if (selectedFiles.length > 3) {
      alert("Maximum 3 files allowed");
      return;
    }

    const formData = new FormData();
    for (let file of selectedFiles) {
      formData.append("files", file);
    }

    try {
      setLoading(true);

      const res = await api.post("/api/contracts/upload", formData);

      console.log("UPLOAD RESPONSE:", res.data);
      alert("UPLOAD RESPONSE RECEIVED");

      // ✅ KEEP FULL CONTRACT OBJECTS
      setBatchId(res.data.batch_id);
      setContracts(res.data.contracts);

    } catch (err) {
      console.error("UPLOAD ERROR:", err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>1️⃣ Upload Contracts</h2>

      <input
        type="file"
        multiple
        accept="application/pdf"
        onChange={handleFileChange}
      />

      <br /><br />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload Contracts"}
      </button>
    </div>
  );
}

export default Upload;
