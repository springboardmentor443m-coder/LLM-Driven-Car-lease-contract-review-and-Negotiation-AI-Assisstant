import React from 'react';
import { Loader2 } from 'lucide-react';

const Loader = ({ text }) => {
    return (
        <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            padding: '20px' 
        }}>
            {/* Animated Icon */}
            <div style={{ position: 'relative', width: '60px', height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {/* Outer pulsing ring */}
                <div style={{
                    position: 'absolute',
                    inset: 0,
                    border: '2px solid var(--primary)',
                    borderRadius: '50%',
                    opacity: 0.5,
                    animation: 'ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite'
                }}></div>
                
                {/* Spinning Icon */}
                <Loader2 
                    size={32} 
                    color="#10b981" 
                    style={{ animation: 'spin 2s linear infinite' }} 
                />
            </div>

            {/* Loading Text */}
            <h4 style={{ 
                color: 'white', 
                marginTop: '16px', 
                fontWeight: '500',
                letterSpacing: '0.5px' 
            }}>
                {text || "Processing..."}
            </h4>

            {/* Inline Keyframes for this component */}
            <style>
                {`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                @keyframes ping {
                    75%, 100% { transform: scale(2); opacity: 0; }
                }
                `}
            </style>
        </div>
    );
};

export default Loader;