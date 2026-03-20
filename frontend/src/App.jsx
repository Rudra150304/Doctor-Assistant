//doctor-assistant/frontend/src/App.jsx
import { useState } from 'react';
import './App.css';
import RoleSelect from './components/RoleSelect';
import DoctorView from './components/DoctorView';
import PatientView from './components/PatientView';

function App() {
  const [role, setRole] = useState(null); // null | 'doctor' | 'patient'

  if (!role) return <RoleSelect onSelect={setRole} />;
  if (role === 'doctor') return <DoctorView onSwitchRole={() => setRole(null)} />;
  if (role === 'patient') return <PatientView onSwitchRole={() => setRole(null)} />;
}

export default App;
