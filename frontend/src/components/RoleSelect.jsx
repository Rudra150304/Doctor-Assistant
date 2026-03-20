//doctor-assistant/frontend/src/components/RoleSelect.jsx
function RoleSelect({ onSelect }) {
  return (
    <div className="role-select-container">
      <div className="role-select-card">
        <div className="brand">
          <span className="brand-icon">⚕️</span>
          <h1>Doctor Assistant</h1>
          <p>Connecting Patients & Doctors</p>
        </div>

        <h2>Who are you today?</h2>
        <p className="role-desc">Choose your role to get a personalized experience.</p>

        <div className="role-options">
          <button className="role-option doctor-option" onClick={() => onSelect('doctor')}>
            <div className="role-option-icon">🩺</div>
            <div className="role-option-content">
              <strong>I'm a Doctor</strong>
              <span>Manage appointments, view stats, and assist patients</span>
            </div>
            <span className="role-arrow">→</span>
          </button>

          <button className="role-option patient-option" onClick={() => onSelect('patient')}>
            <div className="role-option-icon">🏥</div>
            <div className="role-option-content">
              <strong>I'm a Patient</strong>
              <span>Book appointments, ask questions, and get support</span>
            </div>
            <span className="role-arrow">→</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default RoleSelect;
