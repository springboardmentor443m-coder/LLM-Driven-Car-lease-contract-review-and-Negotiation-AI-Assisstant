import React from 'react';
import { Link } from 'react-router-dom';
import SLAView from '../components/SLAView'; 

// Receive analysisData and rawText as PROPS from App.js
const ContractSummary = ({ analysisData, rawText }) => { 

  // Check if data exists in the App.js state
  if (!analysisData) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '50px' }}>
        <h2 style={{ color: '#ef4444' }}>No Contract Data Found</h2>
        <p style={{ color: '#9ca3af' }}>Please upload a contract on the Home page first.</p>
        <Link to="/" style={{ color: '#10b981', textDecoration: 'none', fontWeight: 'bold' }}>
          &larr; Go to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="page-container">
      <h2 className="page-title">Contract Analysis Summary</h2>
      
      <div className="home-card" style={{ marginBottom: '24px' }}>
        <h3 style={{ color: '#10b981', marginTop: 0 }}>Executive Summary</h3>
        <p style={{ color: '#d1d5db', lineHeight: '1.6' }}>
          {analysisData.executive_summary || "No summary available."}
        </p>
      </div>

      {/* Pass the data down to the component */}
      <SLAView analysisData={analysisData} rawText={rawText} />
      
      <div style={{ textAlign: 'right', marginTop: '20px' }}>
        <Link 
          to="/valuation" 
          className="nav-item active" 
          style={{
            display: 'inline-block', 
            padding: '10px 20px', 
            background: '#374151', 
            borderRadius: '8px', 
            color: 'white', 
            textDecoration: 'none',
            border: '1px solid #4b5563'
          }}
        >
          Next: Vehicle Valuation &rarr;
        </Link>
      </div>
    </div>
  );
};

export default ContractSummary;