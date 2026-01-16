import React from 'react';
import { Link } from 'react-router-dom';
import { Target, DollarSign, Activity, ShieldCheck, CheckCircle } from 'lucide-react';

const PricePrediction = ({ analysisData }) => {
  const sla = analysisData?.sla_extraction || {};
  const market = analysisData?.market_data || {};
  
  const parseValue = (val) => {
    if (!val) return 0;
    const cleaned = String(val).replace(/[$,]/g, '');
    return parseFloat(cleaned) || 0;
  };
  
  const buyout_from_contract = parseValue(sla?.residual_value) || parseValue(sla?.buyout_price) || 0;
  const market_price = market?.market_average || 0;
  const lease_term = parseValue(sla?.lease_term_months) || 36;
  const mileage = analysisData?.mileage || 15000;
  
  let equity = market_price - buyout_from_contract;
  const isPositiveEquity = equity > 0;
  const diff_pct = market_price > 0 ? ((buyout_from_contract - market_price) / market_price) * 100 : 0;
  const predicted_purchase_price = market_price * 1.07;

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <h2 className="page-title">Market Valuation & Equity Analysis</h2>

      {/* TOP ROW */}
      <div className="grid-2-col" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* CARD 1: Equity/Variance */}
        <div className="home-card" style={{ 
          textAlign: 'center', 
          border: isPositiveEquity ? '2px solid #10b981' : '2px solid #ef4444',
          background: 'rgba(17, 24, 39, 0.8)',
          padding: '24px'
        }}>
           <div style={{display:'flex', alignItems:'center', gap:'10px', color:'#9ca3af', justifyContent:'center'}}>
             <Target size={20}/> {isPositiveEquity ? "ESTIMATED EQUITY" : "PRICE VARIANCE"}
           </div>
           <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: isPositiveEquity ? '#10b981' : '#ef4444', margin: '15px 0' }}>
             {equity !== 0 ? `${isPositiveEquity ? '+' : ''}$${Math.abs(equity).toLocaleString(undefined, {maximumFractionDigits: 0})}` : "---"}
           </div>
           <div style={{ background: isPositiveEquity ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', padding: '10px', borderRadius: '8px', color: '#d1d5db', fontSize: '0.85rem' }}>
              {isPositiveEquity 
                ? `The buyout is ${Math.abs(diff_pct).toFixed(1)}% below market value.` 
                : `The buyout is ${diff_pct.toFixed(1)}% higher than market value.`}
           </div>
        </div>

        {/* CARD 2: Live Market Data */}
        <div className="home-card" style={{ padding: '24px' }}>
           <h3 style={{marginTop:0, display:'flex', gap:'10px', alignItems:'center'}}>
             <DollarSign color="#10b981"/> Live Market Data
           </h3>
           <div style={{marginBottom: '15px', padding: '10px', background: '#1f2937', borderRadius: '6px', fontSize: '0.85rem'}}>
             <Activity size={14} style={{marginRight: '5px'}}/> 
             Verified for VIN: <strong>{analysisData?.vin || 'N/A'}</strong> at <strong>{mileage.toLocaleString()} miles</strong>
           </div>
           <ul style={{lineHeight:'2.2', color:'#d1d5db', listStyle: 'none', padding: 0}}>
             <li style={{display:'flex', justifyContent:'space-between'}}>
               <span>Current Market Value:</span> 
               <span style={{color: '#fff', fontWeight: 'bold'}}>${market_price.toLocaleString()}</span>
             </li>
             <li style={{display:'flex', justifyContent:'space-between'}}>
               <span>Contract Buyout:</span> 
               <span style={{color: '#fff'}}>${buyout_from_contract.toLocaleString()}</span>
             </li>
           </ul>
        </div>
      </div>

      {/* BOTTOM ROW (Centered Recommendation) */}
      <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
        <div className="home-card" style={{ 
          width: '100%', 
          maxWidth: 'calc(50% - 10px)', // Ensures it stays exactly the size of one card above
          textAlign: 'center',
          border: isPositiveEquity ? '2px solid #10b981' : '2px solid #3b82f6', 
          background: isPositiveEquity ? 'rgba(16, 185, 129, 0.1)' : 'rgba(30, 58, 138, 0.2)',
          padding: '24px'
        }}>
           <div style={{display:'flex', alignItems:'center', gap:'10px', color:'#9ca3af', justifyContent:'center', marginBottom: '10px'}}>
             {isPositiveEquity ? <CheckCircle size={20} color="#10b981"/> : <ShieldCheck size={20} color="#3b82f6"/>}
             {isPositiveEquity ? "STRATEGIC RECOMMENDATION" : "FAIR PURCHASE PREDICTION"}
           </div>
           <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#fff', marginBottom: '10px'}}>
             {isPositiveEquity 
                ? "EXECUTE BUYOUT" 
                : `$${predicted_purchase_price.toLocaleString(undefined, {maximumFractionDigits: 0})}`
             }
           </div>
           <p style={{fontSize: '0.9rem', color: '#d1d5db', margin: 0}}>
             {isPositiveEquity 
               ? `Your contract is $${Math.abs(equity).toLocaleString()} cheaper than market. Buy the car.` 
               : "Current buyout is overpriced. Negotiate toward this market-realistic target."}
           </p>
        </div>
      </div>
      
      <div style={{textAlign:'right', marginTop: '10px'}}>
        <Link to="/chat" className="nav-item active" style={{display:'inline-block', padding:'10px 20px', background:'#374151', borderRadius:'8px', color:'white', textDecoration:'none'}}>
            Next: Review Negotiation Strategy &rarr;
        </Link>
      </div>
    </div>
  );
};

export default PricePrediction;