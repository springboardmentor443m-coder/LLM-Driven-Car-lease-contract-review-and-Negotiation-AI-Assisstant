import React from 'react';

const FairnessScore = ({ analysis }) => {
  const score = analysis?.score || 0;
  const label = analysis?.assessment || "Fairness Rating";

  let color = '#ef4444'; // Red
  if (score >= 75) color = '#10b981'; // Green
  else if (score >= 50) color = '#f59e0b'; // Yellow

  const radius = 50;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: '120px', height: '120px' }}>
        <svg height="120" width="120" style={{ transform: 'rotate(-90deg)' }}>
          <circle stroke="#374151" strokeWidth={stroke} fill="transparent" r={normalizedRadius} cx={radius + 10} cy={radius + 10} />
          <circle stroke={color} fill="transparent" strokeWidth={stroke} strokeDasharray={circumference + ' ' + circumference} style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.5s ease-in-out' }} strokeLinecap="round" r={normalizedRadius} cx={radius + 10} cy={radius + 10} />
        </svg>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: color }}>{score}</div>
          <div style={{ fontSize: '0.7rem', color: '#9ca3af' }}>/ 100</div>
        </div>
      </div>
      <div style={{ marginTop: '10px', color: '#d1d5db', fontSize: '0.9rem', fontWeight: '500' }}>{label}</div>
    </div>
  );
};
export default FairnessScore;