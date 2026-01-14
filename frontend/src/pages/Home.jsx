import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Search, Loader2, FileText } from 'lucide-react';
import { uploadFile } from '../api/ocr';
import { runFullAnalysis } from '../api/llm';

const Home = ({ setAnalysisData, setRawText, setVinData }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [vinInput, setVinInput] = useState("");

  // --- HELPER: VIN SANITIZER ---
  const sanitizeVIN = (vin) => {
    if (!vin) return null;

    let clean = vin.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();

    // Fix common OCR issue: leading extra '4'
    if (clean.length === 18 && clean.startsWith('4')) {
      clean = clean.substring(1);
    }

    // Fallback: trim to last 17 chars
    if (clean.length > 17) {
      clean = clean.substring(clean.length - 17);
    }

    return clean;
  };

  // --- FLOW 1: DOCUMENT UPLOAD ---
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setStatusMsg("Scanning document (OCR)...");

    try {
      const ocrRes = await uploadFile(file);
      if (ocrRes.error) throw new Error(ocrRes.error);
      setRawText(ocrRes.text);

      setStatusMsg("Analyzing contract & checking vehicle databases...");

      const aiRes = await runFullAnalysis(ocrRes.text);
      if (aiRes.error) throw new Error(aiRes.error);

      setAnalysisData(aiRes);

      // ✅ Correct VIN priority (NHTSA first)
      let rawVin =
        aiRes.nhtsa_details?.vin ||
        aiRes.vehicle_details?.vin ||
        aiRes.vin;

      const validVin = sanitizeVIN(rawVin);
      const details = aiRes.vehicle_details || aiRes.nhtsa_details || null;

      if (validVin && validVin.length === 17) {
        setVinData({ vin: validVin, details });
      }

      setStatusMsg("Done! Redirecting to Summary...");
      navigate('/summary');

    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
      setStatusMsg("");
    }
  };

  // --- FLOW 2: DIRECT VIN SEARCH ---
  const handleVinSearch = async () => {
    const cleanVin = sanitizeVIN(vinInput);

    if (!cleanVin || cleanVin.length !== 17) {
      alert("VIN must be exactly 17 valid characters.");
      return;
    }

    setLoading(true);
    setStatusMsg("Fetching Vehicle Details from NHTSA...");

    try {
      // Use the valuation endpoint to get complete data (NHTSA + market price)
      const response = await fetch(`http://localhost:8000/vin/valuation/${cleanVin}`);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`VIN lookup failed: ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();

      // Set both vinData and analysisData for complete information
      setVinData({ vin: cleanVin, details: data.vehicle_details });
      setAnalysisData(data);
      setRawText("");

      navigate('/valuation');

    } catch (err) {
      // Provide more helpful error messages
      let errorMessage = err.message;
      if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
        errorMessage = "Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000";
      }
      alert(errorMessage);
    } finally {
      setLoading(false);
      setStatusMsg("");
    }
  };

  return (
    <div className="page-container">
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1 className="page-title" style={{ justifyContent: 'center' }}>
          AI Auto Lease Auditor
        </h1>
        <p style={{ color: '#9ca3af' }}>
          Upload a contract or search a VIN to detect hidden fees and fair value.
        </p>
      </header>

      <div className="grid-2-col">
        {/* CARD 1: UPLOAD */}
        <div className="home-card upload-zone">
          <h3 style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: 0 }}>
            <FileText color="#10b981" /> Analyze Contract
          </h3>

          <div className="upload-dashed-area" style={{
            border: '2px dashed #4b5563',
            borderRadius: '12px',
            padding: '40px',
            textAlign: 'center',
            background: 'rgba(255,255,255,0.02)',
            cursor: 'pointer',
            position: 'relative',
            marginTop: '16px'
          }}>
            {loading ? (
              <div style={{ textAlign: 'center' }}>
                <Loader2 className="animate-spin" size={40} color="#10b981" style={{ margin: '0 auto 10px' }} />
                <p style={{ color: 'white' }}>{statusMsg}</p>
              </div>
            ) : (
              <>
                <Upload size={32} color="#10b981" style={{ marginBottom: '10px' }} />
                <h4 style={{ margin: 0, color: 'white' }}>Click to Upload PDF/Image</h4>
                <p style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                  We extract terms, VIN, and market data automatically.
                </p>
              </>
            )}

            <input
              type="file"
              onChange={handleFileUpload}
              disabled={loading}
              accept=".pdf,.png,.jpg,.jpeg"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                opacity: 0,
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            />
          </div>
        </div>

        {/* CARD 2: VIN SEARCH */}
        <div className="home-card">
          <h3 style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: 0 }}>
            <Search color="#10b981" /> Quick VIN Check
          </h3>

          <p style={{ color: '#9ca3af', fontSize: '0.9rem', marginBottom: '20px' }}>
            Check NHTSA specs and Market Value without a contract.
          </p>

          <input
            type="text"
            placeholder="Enter 17-Char VIN"
            value={vinInput}
            onChange={(e) => setVinInput(e.target.value.toUpperCase())}
            maxLength={18}
            style={{
              width: '100%',
              padding: '12px',
              background: '#374151',
              border: '1px solid #4b5563',
              borderRadius: '8px',
              color: 'white',
              marginBottom: '15px',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />

          <button
            onClick={handleVinSearch}
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              background: '#10b981',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              fontWeight: 'bold',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? "Searching..." : "Check Value"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;
