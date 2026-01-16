import React from 'react';
import { Link, useLocation } from 'react-router-dom'; // 1. Added useLocation
import SLAView from '../components/SLAView'; 

const ContractSummary = () => { // 2. Removed props from here
  const location = useLocation();
  
  // 3. CATCH the data from the Home page's suitcase
  const { analysisData, rawText } = location.state || {};

  // DEBUG: Check your browser console (F12) to see if data exists here
  console.log("Summary Page Suitcase:", analysisData);

  if (!analysisData) {
    return (
      <div className="page-container">
        <h2>No Data found in suitcase.</h2>
        <p>Please upload the contract on the Home page first.</p>
        <Link to="/" style={{color:'#10b981'}}>Go Home</Link>
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

      <SLAView analysisData={analysisData} rawText={rawText} />
      
      <div style={{textAlign:'right', marginTop:'20px'}}>
        <Link 
          to="/valuation" 
          state={{ analysisData, rawText }} // 4. PASS the suitcase to Valuation
          className="nav-item active" 
          style={{
            display:'inline-block', 
            padding:'10px 20px', 
            background:'#374151', 
            borderRadius:'8px', 
            color:'white', 
            textDecoration:'none'
          }}
        >
          Next: Vehicle Valuation &rarr;
        </Link>
      </div>
    </div>
  );
};

export default ContractSummary;