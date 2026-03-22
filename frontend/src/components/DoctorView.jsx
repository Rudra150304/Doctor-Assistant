//doctor-assistant/frontend/src/components/DoctorView.jsx
import { useState, useRef, useEffect } from 'react';

function DoctorView({ user, onSwitchRole }) {
  const SESSION_ID = `doc_${user?.doctor_id}`;

  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hello, Doctor. I can help you manage appointments, check patient records, and more." }
  ]);

  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const endRef = useRef(null);

  // 🔥 Chat scroll
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 🔥 Notifications polling (NEW)
  useEffect(() => {
    if (!user?.doctor_id) return;

    const fetchNotifications = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/notifications/${user.doctor_id}`);
        const data = await res.json();

        setNotifications(data.notifications || []);
      } catch (err) {
        console.error("Notification error:", err);
      }
    };

    fetchNotifications();

    const interval = setInterval(fetchNotifications, 5000);

    return () => clearInterval(interval);
  }, [user]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    setMessages(prev => [...prev, { role: 'user', text }]);
    setInputValue('');
    setIsTyping(true);

    try {
      const url = new URL('/chat', import.meta.env.VITE_API_URL);
      url.searchParams.append('session_id', SESSION_ID);
      url.searchParams.append('message', text);

      const res = await fetch(url, { method: 'POST' });
      if (!res.ok) throw new Error('Network error');

      const data = await res.json();

      setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);

    } catch {
      setMessages(prev => [...prev, {
        role: 'system',
        text: 'Could not reach the backend server.'
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const quickMessage = (msg) => sendMessage(msg);

  const quickActions = [
    { label: "📊 Today's Appointments", msg: "How many appointments today?" },
    { label: "👥 Patients Yesterday", msg: "How many patients yesterday?" },
    { label: "📋 Today's Schedule", msg: "Show today's schedule" },
  ];

  return (
    <div className="view-container doctor-view">

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="role-badge doctor-badge">🩺</div>
          <div>
            <h2>Doctor Panel</h2>
            <p className="role-subtitle">Dr. {user?.doctor_id}</p>
          </div>
        </div>

        {/* Quick Actions */}
        <section className="quick-actions">
          <h3>Quick Actions</h3>
          <div className="actions-list">
            {quickActions.map((action, i) => (
              <button
                key={i}
                className="action-button"
                onClick={() => quickMessage(action.msg)}
              >
                {action.label}
              </button>
            ))}
          </div>
        </section>

        {/* 🔥 Notifications */}
        <section className="notifications-panel">
          <h3>Notifications</h3>
          <div className="notifications-list">
            {notifications.length === 0 ? (
              <p className="no-notif">No notifications yet</p>
            ) : (
              notifications.slice(0, 5).map((n, i) => (
                <div key={i} className="notif-card doctor-notif">
                  <span className="notif-time">{n.time}</span>
                  <p>{n.text}</p>
                </div>
              ))
            )}
          </div>
        </section>

        <button className="switch-role-btn" onClick={onSwitchRole}>
          ⇄ Switch Role
        </button>
      </aside>

      {/* Chat */}
      <main className="chat-main">
        <div className="chat-header doctor-header">
          <div className="header-left">
            <h1>Doctor Assistant</h1>
            <span className="header-sub">Powered by AI</span>
          </div>
          <span className="status-badge">
            <span className="dot"></span> Online
          </span>
        </div>

        <div className="messages-area">
          {messages.map((msg, i) => (
            <div key={i} className={`msg-wrapper ${msg.role}`}>
              <div className="msg-bubble">
                {msg.role === 'assistant' && <span className="msg-icon">🩺</span>}
                <p>{msg.text}</p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="msg-wrapper assistant">
              <div className="msg-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}

          <div ref={endRef} />
        </div>

        {/* Input */}
        <form className="input-area" onSubmit={handleSubmit}>
          <input
            className="chat-input"
            type="text"
            placeholder="Ask about appointments, patients, schedules..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isTyping}
          />

          <button
            type="submit"
            className="send-btn doctor-send"
            disabled={!inputValue.trim() || isTyping}
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default DoctorView;
