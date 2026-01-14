import React from 'react';
import { FileText, Check, X, AlertCircle } from 'lucide-react';

const SLAView = ({ analysisData }) => {
  const sla = analysisData?.sla_extraction || {};

  // This list matches the EXACT keys from your backend llm_service.py
  const terms = [
    { key: 'monthly_payment', label: 'Monthly Payment' },
    { key: 'down_payment', label: 'Down Payment' },
    { key: 'lease_term_months', label: 'Lease Term' },
    { key: 'interest_rate_apr', label: 'Interest Rate / MF' },
    { key: 'residual_value', label: 'Residual Value' },
    { key: 'mileage_allowance_per_year', label: 'Annual Mileage' },
    { key: 'excess_mileage_fee', label: 'Excess Mileage Fee' },
    { key: 'early_termination_fee', label: 'Termination Fee' },
    { key: 'buyout_price', label: 'Buyout Option' },
    { key: 'maintenance_responsibilities', label: 'Maintenance' },
    { key: 'warranty_coverage', label: 'Warranty' },
    { key: 'penalties_late_fees', label: 'Late Fees' },
  ];

  return (
    <div className="sla-container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
      {terms.map((item) => {
        const value = sla[item.key];
        // If value is missing or "Not Mentioned", show warning style
        const isMissing = !value || value.toLowerCase().includes('not mentioned');
        
        return (
          <div key={item.key} className="sla-card" style={{ 
            background: 'var(--bg-card)', 
            padding: '16px', 
            borderRadius: '12px',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#9ca3af', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                {item.label}
              </span>
              {isMissing ? <AlertCircle size={16} color="#ef4444" /> : <Check size={16} color="#10b981" />}
            </div>
            
            <div style={{ 
              fontSize: '1.1rem', 
              fontWeight: '600', 
              color: isMissing ? '#ef4444' : 'white' 
            }}>
              {value || "Not Found"}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SLAView;