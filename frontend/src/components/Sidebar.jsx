import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, FileText, Car, DollarSign, MessageSquare, Zap } from 'lucide-react';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      {/* Logo Section */}
      <div className="logo-area" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
            background: 'linear-gradient(135deg, #10b981, #047857)',
            padding: '8px',
            borderRadius: '8px',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
            <Zap size={20} color="white" fill="white" />
        </div>
        <div>
            <h2 style={{color: 'white', fontWeight: 'bold', fontSize: '1.1rem', margin: 0}}>AutoLease AI</h2>
            <p style={{fontSize: '0.75rem', color: '#9ca3af', margin: 0}}>Contract Intelligence</p>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="nav-menu">
        <NavItem to="/" icon={Home} label="Home" />
        <NavItem to="/summary" icon={FileText} label="Contract Summary" />
        <NavItem to="/valuation" icon={Car} label="Vehicle Valuation" />
        <NavItem to="/prediction" icon={DollarSign} label="Price Prediction" />
        <NavItem to="/chat" icon={MessageSquare} label="AI Chatbot" />
      </nav>
    </aside>
  );
};

// Helper Component for Links
const NavItem = ({ to, icon: Icon, label }) => (
  <NavLink 
    to={to} 
    className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
  >
    <Icon size={18} />
    <span>{label}</span>
  </NavLink>
);

export default Sidebar;