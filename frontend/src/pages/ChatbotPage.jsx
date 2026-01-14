import React from 'react';
import ChatBot from '../components/ChatBot';
import { useLocation } from 'react-router-dom';

const ChatbotPage = ({ contractText }) => { 
  // 1. Try to get text from Props (passed from App.jsx) OR the Router State (Suitcase)
  const location = useLocation();
  const activeText = contractText || location.state?.rawText || "";

  return (
    <div className="page-container" style={{ height: '85vh', display: 'flex', flexDirection: 'column' }}>
      <h2 className="page-title">AI Negotiation Assistant</h2>
      
      {/* 2. Just the Chatbot (Full Height) */}
      <div style={{ flex: 1 }}>
         <ChatBot initialContext={activeText} />
      </div>
    </div>
  );
};

export default ChatbotPage;