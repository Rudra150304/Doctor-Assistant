// doctor-assistant/frontend/src/App.jsx

import { useState } from 'react';
import './App.css';
import RoleSelect from './components/RoleSelect';
import DoctorView from './components/DoctorView';
import PatientView from './components/PatientView';

function App() {
  const [role, setRole] = useState(null);
  const [user, setUser] = useState(null);

  // ✅ login handler
  const handleSelect = (role, userData) => {
    setRole(role);
    setUser(userData);
  };

  // ✅ logout handler (FIXED)
  const handleLogout = () => {
    setRole(null);
    setUser(null);
  };

  // ✅ no role → show login
  if (!role) {
    return <RoleSelect onSelect={handleSelect} />;
  }

  // ✅ doctor view
  if (role === "doctor") {
    return (
      <DoctorView
        user={user}
        onSwitchRole={handleLogout}
      />
    );
  }

  // ✅ patient view
  if (role === "patient") {
    return (
      <PatientView
        user={user}
        onSwitchRole={handleLogout}
      />
    );
  }

  // fallback (just in case)
  return null;
}

export default App;
