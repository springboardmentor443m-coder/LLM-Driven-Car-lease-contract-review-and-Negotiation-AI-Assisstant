import React, { useState } from "react";

function VinLookup() {
  const [vin, setVin] = useState("");
  const [vehicleData, setVehicleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLookup = async () => {
    if (!vin) {
      alert("Please enter a VIN number");
      return;
    }

    setLoading(true);
    setError("");
    setVehicleData(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/vin-lookup?vin=${vin}`
      );

      const data = await response.json();

      if (response.ok) {
        setVehicleData(data);
      } else {
        setError(data.error || "VIN lookup failed");
      }
    } catch (err) {
      setError("Backend server not running");
    }

    setLoading(false);
  };

  return (
    <div style={{ border: "1px solid #999", padding: "15px" }}>
      <h2>VIN Lookup</h2>

      <input
        type="text"
        placeholder="Enter VIN number"
        value={vin}
        onChange={(e) => setVin(e.target.value)}
        style={{ width: "300px" }}
      />

      <br /><br />

      <button onClick={handleLookup} disabled={loading}>
        {loading ? "Checking..." : "Check VIN"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {vehicleData && (
        <div style={{ marginTop: "15px" }}>
          <h3>Vehicle Information</h3>
          <ul>
            <li><strong>VIN:</strong> {vehicleData.VIN}</li>
            <li><strong>Make:</strong> {vehicleData.Make}</li>
            <li><strong>Model:</strong> {vehicleData.Model}</li>
            <li><strong>Year:</strong> {vehicleData.Year}</li>
            <li><strong>Recall Info:</strong> {vehicleData.RecallInfo}</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default VinLookup;
