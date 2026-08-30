import { useState } from "react";

const API_BASE = "https://phishing-detector-a3ek.onrender.com";

export default function LoginScreen({ onLogin }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem("admin_token", data.token);
        onLogin(data.token);
      } else {
        setError(data.message || "Login failed");
      }
    } catch (err) {
      setError("Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <form onSubmit={handleSubmit} style={{
        background: "var(--panel)", border: "1px solid var(--line)",
        borderRadius: 8, padding: "36px 32px", width: 320,
      }}>
        <div className="mono" style={{
          fontSize: 10, letterSpacing: "1px", textTransform: "uppercase",
          color: "var(--signal)", marginBottom: 6,
        }}>
          Hybrid Phishing Detector
        </div>
        <h1 style={{ margin: "0 0 22px", fontSize: 20, fontWeight: 600 }}>Admin Console</h1>
        <label className="mono" style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase" }}>
          Password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoFocus
          style={{
            width: "100%", marginTop: 6, marginBottom: 14, background: "var(--ink)",
            border: "1px solid var(--line)", borderRadius: 4, padding: "10px 12px",
            color: "var(--text)", fontSize: 13, outline: "none",
          }}
        />
        {error && (
          <div style={{ color: "var(--alert)", fontSize: 12, marginBottom: 14 }}>{error}</div>
        )}
        <button
          type="submit"
          disabled={loading}
          className="mono"
          style={{
            width: "100%", background: "var(--signal)", color: "var(--ink)",
            border: "none", borderRadius: 4, padding: "10px", fontSize: 11,
            fontWeight: 700, letterSpacing: "0.6px", textTransform: "uppercase",
            cursor: "pointer", opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? "Verifying…" : "Sign In"}
        </button>
      </form>
    </div>
  );
}
