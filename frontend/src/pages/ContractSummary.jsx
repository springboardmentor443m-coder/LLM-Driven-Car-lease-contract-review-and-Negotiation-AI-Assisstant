import React from 'react';
import { Link } from 'react-router-dom';
import SLAView from '../components/SLAView'; 

const ContractSummary = ({ analysisData, rawText }) => {
  if (!analysisData) {
     return <div className="page-container"><h2>No Data. Please Upload a Contract.</h2><Link to="/" style={{color:'#10b981'}}>Go Home</Link></div>;
  }

  return (
    <div className="page-container">
      <h2 className="page-title">Contract Analysis Summary</h2>
      
      {/* Executive Summary Box */}
      <div className="home-card" style={{ marginBottom: '24px' }}>
        <h3 style={{ color: '#10b981', marginTop: 0 }}>Executive Summary</h3>
        <p style={{ color: '#d1d5db', lineHeight: '1.6' }}>
          {analysisData.executive_summary || "No summary available."}
        </p>
      </div>

      {/* SLA Terms (Reusing your SLAView component) */}
      <SLAView analysisData={analysisData} rawText={rawText} />
      
      <div style={{textAlign:'right', marginTop:'20px'}}>
        <Link 
                  to="/valuation" 
                  state={{ analysisData, rawText }} // <--- ADD THIS LINE (The Suitcase)
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