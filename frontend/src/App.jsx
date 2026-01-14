import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar'; // 1. Import the Sidebar
import Home from './pages/Home';
import ContractSummary from './pages/ContractSummary';
import VehicleValuation from './pages/VehicleValuation';
import PricePrediction from './pages/PricePrediction';
import ChatbotPage from './pages/ChatbotPage';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [rawText, setRawText] = useState("");
  const [vinData, setVinData] = useState(null);

  return (
    <Router>
      {/* 2. Create a layout container to hold Sidebar + Content */}
      <div className="app-layout" style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar />

        <main className="main-content" style={{ flex: 1, overflowY: 'auto' }}>
          <Routes>
            <Route path="/" element={<Home setAnalysisData={setAnalysisData} setRawText={setRawText} setVinData={setVinData} />} />
            <Route path="/summary" element={<ContractSummary analysisData={analysisData} rawText={rawText} />} />
            <Route path="/valuation" element={<VehicleValuation analysisData={analysisData} vinData={vinData} setVinData={setVinData} />} />
            <Route path="/prediction" element={<PricePrediction analysisData={analysisData} />} />
            <Route path="/chat" element={<ChatbotPage contractText={rawText} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;