//doctor-assistant/frontend/src/components/RoleSelect.jsx
import { useState } from "react";

function RoleSelect({ onSelect }) {
  const [role, setRole] = useState(null);

  const [doctorId, setDoctorId] = useState("");
  const [password, setPassword] = useState("");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const handleDoctorLogin = async () => {
    const res = await fetch("/login/doctor", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        doctor_id: Number(doctorId),
        password
      })
    });

    const data = await res.json();

    if (data.success) {
      onSelect("doctor", { doctor_id: data.doctor_id });
    } else {
      alert(data.message);
    }
  };

  const handlePatientLogin = async () => {
    const res = await fetch("/login/patient", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name, email })
    });

    const data = await res.json();

    if (data.success) {
      onSelect("patient", { name, email });
    }
  };

  // ================= UI =================

  return (
    <div className="role-select-container">
      <div className="role-select-card">

        {/* BRAND */}
        <div className="brand">
          <span className="brand-icon">⚕️</span>
          <h1>Doctor Assistant</h1>
          <p>Connecting Patients & Doctors</p>
        </div>

        {/* ================= ROLE SELECT ================= */}
        {!role && (
          <>
            <h2>Who are you today?</h2>
            <p className="role-desc">
              Choose your role to get a personalized experience.
            </p>

            <div className="role-options">
              <button
                className="role-option doctor-option"
                onClick={() => setRole("doctor")}
              >
                <div className="role-option-icon">🩺</div>
                <div className="role-option-content">
                  <strong>I'm a Doctor</strong>
                  <span>Manage appointments & stats</span>
                </div>
                <span className="role-arrow">→</span>
              </button>

              <button
                className="role-option patient-option"
                onClick={() => setRole("patient")}
              >
                <div className="role-option-icon">🏥</div>
                <div className="role-option-content">
                  <strong>I'm a Patient</strong>
                  <span>Book appointments easily</span>
                </div>
                <span className="role-arrow">→</span>
              </button>
            </div>
          </>
        )}

        {/* ================= DOCTOR LOGIN ================= */}
        {role === "doctor" && (
          <>
            <h2>Doctor Login</h2>
            <p className="role-desc">Enter your credentials</p>

            <div className="role-options">
              <input
                className="chat-input"
                placeholder="Doctor ID"
                value={doctorId}
                onChange={(e) => setDoctorId(e.target.value)}
              />

              <input
                className="chat-input"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />

              <button
                className="send-btn doctor-send"
                onClick={handleDoctorLogin}
              >
                Login
              </button>

              <button
                className="switch-role-btn"
                onClick={() => setRole(null)}
              >
                ← Back
              </button>
            </div>
          </>
        )}

        {/* ================= PATIENT LOGIN ================= */}
        {role === "patient" && (
          <>
            <h2>Patient Login</h2>
            <p className="role-desc">Enter your details</p>

            <div className="role-options">
              <input
                className="chat-input"
                placeholder="Your Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />

              <input
                className="chat-input"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

              <button
                className="send-btn patient-send"
                onClick={handlePatientLogin}
              >
                Continue
              </button>

              <button
                className="switch-role-btn"
                onClick={() => setRole(null)}
              >
                ← Back
              </button>
            </div>
          </>
        )}

      </div>
    </div>
  );
}

export default RoleSelect;
