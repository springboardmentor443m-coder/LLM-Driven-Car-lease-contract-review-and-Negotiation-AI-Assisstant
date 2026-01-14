import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom'; // Added useNavigate
import { AlertCircle, CheckCircle, Zap, TrendingUp, ArrowRight } from 'lucide-react'; // Added ArrowRight

const VehicleValuation = ({ analysisData: propAnalysisData }) => {
  const navigate = useNavigate(); // Initialize navigate hook
  const location = useLocation();
  const analysisData = propAnalysisData || location.state?.analysisData;

  console.log("analysisData:", analysisData);

  const nhtsa = analysisData?.nhtsa_details || {};
  const rapidapi = analysisData?.rapidapi_details || {};
  const fairness = analysisData?.fairness_score || {};
  const fairnessAnalysis = analysisData?.fairness_analysis || {};
  const flags = fairnessAnalysis?.flags || [];
  const make = nhtsa?.Make || analysisData?.vehicle_details?.make || 'Unknown';
  const model = nhtsa?.Model || analysisData?.vehicle_details?.model || 'Unknown';
  const year = nhtsa?.["Model Year"] || analysisData?.vehicle_details?.year || '—';
  const vin = nhtsa?.VIN || analysisData?.nhtsa_details?.VIN || analysisData?.nhtsa_details?.vin || '—';
  const marketPrice = analysisData?.market_data?.market_average || rapidapi?.average_market_price || 0;
  const score = fairness?.score || 0;
  const rating = fairness?.rating || 'Standard';

  return (
    <div className="page-container">
      <h2 className="page-title">Vehicle Valuation</h2>
      <div className="grid-2-col">
        {/* Card 1: NHTSA Details */}
        <div className="home-card">
          <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: 8, color: '#10b981' }}>
            <Zap size={20} /> NHTSA Details
          </h3>
          <div style={{ marginTop: 15 }}>
            <div style={{ marginBottom: 12 }}>
              <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0, marginBottom: 4 }}>MAKE</p>
              <p style={{ color: '#d1d5db', margin: 0, fontWeight: '500' }}>{make}</p>
            </div>
            <div style={{ marginBottom: 12 }}>
              <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0, marginBottom: 4 }}>MODEL</p>
              <p style={{ color: '#d1d5db', margin: 0, fontWeight: '500' }}>{model}</p>
            </div>
            <div style={{ marginBottom: 12 }}>
              <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0, marginBottom: 4 }}>YEAR</p>
              <p style={{ color: '#d1d5db', margin: 0, fontWeight: '500' }}>{year}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0, marginBottom: 4 }}>VIN</p>
              <p style={{ color: '#10b981', margin: 0, fontWeight: '500', fontSize: '0.9rem', wordBreak: 'break-all' }}>{vin}</p>
            </div>
          </div>
        </div>

        {/* Card 2: Market Price */}
        <div className="home-card" style={{ textAlign: 'center', border: '2px solid #10b981', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ marginTop: 0, color: '#10b981', display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}>
            <TrendingUp size={20} /> Market Price
          </h3>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#10b981', margin: '15px 0' }}>
            ${marketPrice ? marketPrice.toLocaleString() : '—'}
          </div>
          <p style={{ color: '#9ca3af', margin: 0, fontSize: '0.9rem' }}>
            {marketPrice ? 'Estimated market value' : 'Data not available'}
          </p>
        </div>

        {/* Card 3: Fairness Score */}
        <div className="home-card">
          <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: 8, color: score > 60 ? '#10b981' : '#ef4444' }}>
            <CheckCircle size={20} /> Fairness Score
          </h3>
          <div style={{ margin: '20px 0', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', fontWeight: 'bold', color: score > 60 ? '#10b981' : '#ef4444' }}>
              {score}
            </div>
            <div style={{ fontSize: '1.1rem', color: '#d1d5db', marginTop: 10 }}>
              {rating}
            </div>
          </div>
          <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '10px', borderRadius: '8px', color: '#d1d5db', fontSize: '0.85rem', marginTop: 15 }}>
            {fairness?.reasons?.[0] || 'No analysis available'}
          </div>
        </div>

        {/* Card 4: Red Flags */}
        <div className="home-card">
          <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: 8, color: flags.length > 0 ? '#ef4444' : '#10b981' }}>
            <AlertCircle size={20} /> Red Flags
          </h3>
          {flags && flags.length > 0 ? (
            <ul style={{ color: '#d1d5db', lineHeight: '1.8', marginTop: 15, paddingLeft: 20, margin: 0 }}>
              {flags.map((flag, idx) => (
                <li key={idx} style={{ marginBottom: 8, color: '#d1d5db' }}>
                  <span style={{ color: '#ef4444', fontWeight: 'bold' }}>⚠</span> {flag}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: '#9ca3af', marginTop: 15 }}>✓ No significant red flags detected. This appears to be a fair deal.</p>
          )}
        </div>
      </div>

      {/* Corrected Navigation Box */}
      <div className="nav-box-container" style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '30px' }}>
        <button 
          className="btn-next"
          onClick={() => navigate('/prediction', { state: { analysisData: analysisData } })}
          style={{
            backgroundColor: '#10b981',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}
        >
          Next: Price Prediction <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
};

export default VehicleValuation;