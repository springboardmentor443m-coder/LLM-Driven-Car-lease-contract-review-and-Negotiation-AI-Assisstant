import React from 'react';

const FairnessScore = ({ analysis }) => {
    // SAFETY CHECK: Default values if analysis is missing
    const score = analysis?.score || 0;
    const assessment = analysis?.assessment || "No Score Available";

    // Determine color based on score
    let color = '#ef4444'; // Red (Bad)
    if (score >= 80) color = '#10b981'; // Green (Emerald)
    else if (score >= 50) color = '#f59e0b'; // Orange (Average)

    return (
        <div 
            className="card" 
            style={{ 
                textAlign: 'center', 
                marginBottom: '20px',
                background: 'var(--bg-card)', // Dark Card Background
                color: 'var(--text-main)',    // Light Text
                border: '1px solid var(--border-color)',
                borderRadius: '16px',
                padding: '24px'
            }}
        >
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Contract Fairness Score</h3>
            
            <div style={{
                position: 'relative',
                width: '150px',
                height: '150px',
                margin: '0 auto 24px auto',
                borderRadius: '50%',
                // The empty part is now dark grey to match the theme
                background: `conic-gradient(${color} ${score * 3.6}deg, var(--bg-darker) 0deg)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 20px rgba(0,0,0,0.5)'
            }}>
                {/* Inner Circle covering the center */}
                <div style={{
                    width: '120px',
                    height: '120px',
                    borderRadius: '50%',
                    background: 'var(--bg-card)', // Matches container background
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column'
                }}>
                    <span style={{ fontSize: '36px', fontWeight: 'bold', color: color }}>
                        {score}
                    </span>
                    <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>/ 100</span>
                </div>
            </div>

            <p style={{ 
                fontSize: '0.95rem', 
                color: 'var(--text-main)', 
                maxWidth: '90%', 
                margin: '0 auto',
                lineHeight: '1.5'
            }}>
                {assessment}
            </p>
        </div>
    );
};

export default FairnessScore;