//doctor-assistant/frontend/src/components/PatientView.jsx
import { useState, useRef, useEffect } from 'react';

const SESSION_ID = "patient-1";

const SUGGESTIONS = [
  "Check Dr. Sharma availability tomorrow",
  "Book an appointment with Dr. Ahuja tomorrow morning",
  "Show available slots for Dr. Mehta",
  "Book appointment for tomorrow evening",
];


function PatientView({ onSwitchRole }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hello! I'm your personal health assistant. How can I help you today?" }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setShowSuggestions(false);
    setMessages(prev => [...prev, { role: 'user', text }]);
    setInputValue('');
    setIsTyping(true);

    try {
      const url = new URL('/chat', window.location.origin);
      url.searchParams.append('session_id', SESSION_ID);
      url.searchParams.append('message', text);
      const res = await fetch(url, { method: 'POST' });
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);
    } catch {
      setMessages(prev => [...prev, { role: 'system', text: 'Could not reach the backend server.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e) => { e.preventDefault(); sendMessage(inputValue); };

  return (
    <div className="view-container patient-view">
      <main className="chat-main patient-chat-main">
        {/* Top bar */}
        <div className="chat-header patient-header">
          <div className="header-left">
            <div className="role-badge patient-badge">🏥</div>
            <div>
              <h1>Patient Assistant</h1>
              <span className="header-sub">Your Health Companion</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span className="status-badge">
              <span className="dot patient-dot"></span> Online
            </span>
            <button className="switch-role-btn-top" onClick={onSwitchRole}>
              🩺 Doctor View
            </button>
          </div>
        </div>

        <div className="messages-area patient-messages-area">
          {messages.map((msg, i) => (
            <div key={i} className={`msg-wrapper ${msg.role}`}>
              <div className="msg-bubble">
                {msg.role === 'assistant' && <span className="msg-icon patient-icon">🏥</span>}
                <p>{msg.text}</p>
              </div>
            </div>
          ))}

          {/* Suggestion chips shown only at start */}
          {showSuggestions && messages.length === 1 && (
            <div className="suggestions-container">
              <p className="suggestions-label">Try asking:</p>
              <div className="suggestions-grid">
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} className="suggestion-chip" onClick={() => sendMessage(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {isTyping && (
            <div className="msg-wrapper assistant">
              <div className="msg-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form className="input-area" onSubmit={handleSubmit}>
          <input
            className="chat-input"
            type="text"
            placeholder="Ask about appointments, symptoms, prescriptions..."
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            disabled={isTyping}
          />
          <button type="submit" className="send-btn patient-send" disabled={!inputValue.trim() || isTyping}>
            Send
            <svg viewBox="0 0 24 24" fill="none"><path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </button>
        </form>
      </main>
    </div>
  );
}

export default PatientView;
