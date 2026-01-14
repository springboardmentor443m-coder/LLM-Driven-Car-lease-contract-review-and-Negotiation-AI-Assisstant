import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, RefreshCw } from 'lucide-react';
import { sendChatMessage } from '../api/llm'; 

const Chatbot = ({ initialContext }) => {
  // 1. SMART GREETING: Check if we actually have a contract
  const hasContract = initialContext && initialContext.length > 50;
  
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: hasContract 
        ? "Hello! I have the contract details loaded. Ask me about terms, fees, or negotiation strategies." 
        : "Hello! I am your Auto Lease Assistant. I don't see a contract yet, but ask me general questions about market values or lease terms!"
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // 2. SYSTEM PROMPT
      const systemMessage = {
        role: 'system',
        content: `
          You are an expert Car Lease Consultant and Market Analyst.
          
          [UPLOADED CONTRACT DATA]:
          ${initialContext || "No specific contract uploaded. Answer based on general automotive knowledge."}
          
          [INSTRUCTIONS]:
          1. Answer strictly based on the context provided above if available.
          2. If no contract is provided, give general expert advice.
          3. Be concise, professional, and helpful.
        `
      };

      // 3. SEND HISTORY
      const historyPayload = [
        systemMessage,
        ...messages.map(m => ({ role: m.role, content: m.content })),
        userMsg
      ];

      const response = await sendChatMessage(historyPayload, input);
      
      const replyText = response.response || response.reply || "I'm having trouble connecting to the brain.";

      setMessages(prev => [...prev, { role: 'assistant', content: replyText }]);

    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: Could not reach the AI." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div style={{ 
      display: 'flex', flexDirection: 'column', height: '100%', 
      background: 'var(--bg-card)', borderRadius: '16px', border: '1px solid var(--border-color)',
      overflow: 'hidden' 
    }}>
      
      {/* Header */}
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)', background: 'var(--bg-darker)' }}>
        <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1rem', color: 'white' }}>
          <Bot size={20} color="#10b981" />
          {hasContract ? "Contract Analyst Active" : "General Assistant"}
        </h3>
      </div>

      {/* Messages Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ 
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '12px',
              fontSize: '0.9rem',
              lineHeight: '1.5',
              background: msg.role === 'user' ? '#10b981' : 'var(--bg-dark)',
              color: msg.role === 'user' ? 'white' : 'var(--text-main)',
              border: msg.role === 'assistant' ? '1px solid var(--border-color)' : 'none',
              borderBottomRightRadius: msg.role === 'user' ? '2px' : '12px',
              borderBottomLeftRadius: msg.role === 'assistant' ? '2px' : '12px',
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', color: '#9ca3af', fontSize: '0.8rem', display: 'flex', gap: '6px', marginLeft: '10px' }}>
            <RefreshCw size={14} className="animate-spin" /> Thinking...
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Area */}
      <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-darker)' }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={hasContract ? "Ask about specific fees or terms..." : "Ask general lease questions..."}
            style={{
              flex: 1, background: 'var(--bg-input)', border: '1px solid var(--border-color)',
              color: 'white', padding: '10px 16px', borderRadius: '8px', outline: 'none'
            }}
          />
          <button 
            onClick={handleSend}
            disabled={loading}
            style={{
              background: 'var(--primary)', border: 'none', borderRadius: '8px',
              width: '44px', display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1
            }}
          >
            <Send size={20} color="white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;