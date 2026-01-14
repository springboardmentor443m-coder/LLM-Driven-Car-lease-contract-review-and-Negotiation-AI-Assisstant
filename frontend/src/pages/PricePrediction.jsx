import React from 'react';
import { Link } from 'react-router-dom';
import { Target, DollarSign } from 'lucide-react';

const PricePrediction = ({ analysisData }) => {
  const sla = analysisData?.sla_extraction || {};
  const market = analysisData?.market_data || analysisData?.rapidapi_details || {};
  
  // Extract buyout price - check both residual_value and buyout_price fields
  const parseValue = (val) => {
    if (!val) return 0;
    const cleaned = String(val).replace(/[$,]/g, '');
    return parseFloat(cleaned) || 0;
  };
  
  const buyout_from_contract = parseValue(sla?.residual_value) || parseValue(sla?.buyout_price) || 0;
  const market_price = market?.market_average || 0;
  const lease_term = parseValue(sla?.lease_term_months) || 36;
  
  // Calculate PREDICTED buyout based on market depreciation (always)
  let predicted_buyout = 0;
  let buyout_reasoning = "Fair market estimate based on depreciation";
  
  if (market_price > 0) {
    // Calculate fair buyout based on typical depreciation curve
    const depreciation_rate = 1 - (0.60 / (lease_term / 36)); // 60% residual over 36 months
    predicted_buyout = market_price * depreciation_rate;
    
    // Compare to contract buyout if available
    if (buyout_from_contract > 0) {
      const diff = buyout_from_contract - predicted_buyout;
      const diff_pct = (diff / predicted_buyout) * 100;
      if (diff > 0) {
        buyout_reasoning = `Contract: $${buyout_from_contract.toLocaleString('en-US', {maximumFractionDigits: 0})} (${diff_pct.toFixed(1)}% above fair market)`;
      } else {
        buyout_reasoning = `Contract: $${buyout_from_contract.toLocaleString('en-US', {maximumFractionDigits: 0})} (${Math.abs(diff_pct).toFixed(1)}% below fair market)`;
      }
    } else {
      buyout_reasoning = "Estimated based on market depreciation curve";
    }
  }

  return (
    <div className="page-container">
      <h2 className="page-title">Buyout Price Prediction</h2>

      <div className="grid-2-col">
        {/* CARD 1: The Buyout Recommendation */}
        <div className="home-card" style={{ textAlign: 'center', border: '2px solid #10b981' }}>
           <div style={{display:'flex', alignItems:'center', gap:'10px', color:'#9ca3af', justifyContent:'center'}}>
             <Target size={20}/> PREDICTED BUYOUT PRICE
           </div>
           <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#10b981', margin: '15px 0'}}>
             ${predicted_buyout > 0 ? predicted_buyout.toLocaleString('en-US', {maximumFractionDigits: 0}) : "---"}
           </div>
           <div style={{background: 'rgba(16, 185, 129, 0.1)', padding: '10px', borderRadius: '8px', color: '#d1d5db', fontSize: '0.9rem'}}>
              {buyout_reasoning}
           </div>
        </div>

        {/* CARD 2: Market Context */}
        <div className="home-card">
           <h3 style={{marginTop:0, display:'flex', gap:'10px', alignItems:'center'}}>
             <DollarSign color="#10b981"/> Valuation Context
           </h3>
           <ul style={{lineHeight:'2', color:'#d1d5db', listStyle: 'none', padding: 0}}>
             <li><strong>Current Market Price:</strong> ${market?.market_average > 0 ? market.market_average.toLocaleString('en-US', {maximumFractionDigits: 0}) : "N/A"}</li>
             <li><strong>Monthly Lease Payment:</strong> {sla?.monthly_payment || "N/A"}</li>
             <li><strong>Lease Term:</strong> {lease_term} months</li>
             <li><strong>Buyout Option Price:</strong> ${buyout_from_contract > 0 ? buyout_from_contract.toLocaleString('en-US', {maximumFractionDigits: 2}) : "Not specified in contract"}</li>
           </ul>
        </div>
      </div>
      
      <div style={{textAlign:'right', marginTop:'20px'}}>
        <Link to="/chat" className="nav-item active" style={{display:'inline-block', padding:'10px 20px', background:'#374151', borderRadius:'8px', color:'white', textDecoration:'none'}}>
           Next: Ask Chatbot &rarr;
        </Link>
      </div>
    </div>
  );
};

export default PricePrediction;