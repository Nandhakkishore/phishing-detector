import { useState } from "react";
import LoginScreen from "./components/LoginScreen";
import AdminDashboard from "./components/AdminDashboard";
import "./index.css";

function App() {
  const [token, setToken] = useState(localStorage.getItem("admin_token"));

  function handleLogout() {
    localStorage.removeItem("admin_token");
    setToken(null);
  }

  if (!token) {
    return <LoginScreen onLogin={setToken} />;
  }

  return <AdminDashboard onLogout={handleLogout} />;
}

export default App;
