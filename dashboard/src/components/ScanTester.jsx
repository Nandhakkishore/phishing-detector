import { useState } from "react";

const API_BASE = "https://phishing-detector-a3ek.onrender.com";

const COLORS = {
  legitimate: "var(--signal)",
  phishing: "var(--alert)",
  suspicious: "var(--warn)",
};

export default function ScanTester({ onScanComplete }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function runScan() {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json();
      setResult(data);
      onScanComplete?.();
    } catch (err) {
      setError("Could not reach the detection API.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") runScan();
  }

  return (
    <div style={{
      background: "var(--panel)", border: "1px solid var(--line)",
      borderRadius: 6, padding: 20,
    }}>
      <div className="mono" style={{
        fontSize: 10, letterSpacing: "0.8px", textTransform: "uppercase",
        color: "var(--muted)", marginBottom: 14,
      }}>
        Live Scan
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          className="mono"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="https://example.com"
          style={{
            flex: 1, background: "var(--ink)", border: "1px solid var(--line)",
            borderRadius: 4, padding: "10px 12px", color: "var(--text)",
            fontSize: 12.5, outline: "none",
          }}
        />
        <button
          onClick={runScan}
          disabled={loading}
          className="mono"
          style={{
            background: "var(--signal)", color: "var(--ink)", border: "none",
            borderRadius: 4, padding: "0 18px", fontSize: 11, fontWeight: 700,
            letterSpacing: "0.6px", textTransform: "uppercase", cursor: "pointer",
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? "Scanning…" : "Scan"}
        </button>
      </div>

      {error && (
        <div style={{ color: "var(--alert)", fontSize: 12.5, marginTop: 12 }}>{error}</div>
      )}

      {result && (
        <div style={{
          marginTop: 14, paddingTop: 14, borderTop: "1px solid var(--line)",
        }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
            <span className="mono" style={{
              fontSize: 15, fontWeight: 700, textTransform: "uppercase",
              color: COLORS[result.classification] || "var(--text)",
            }}>
              {result.classification}
            </span>
            <span className="mono" style={{ fontSize: 11, color: "var(--muted)" }}>
              {(result.confidence * 100).toFixed(1)}% confidence
            </span>
          </div>
          <ul style={{ margin: "10px 0 0", padding: 0, listStyle: "none" }}>
            {result.reasons.map((r, i) => (
              <li key={i} style={{
                fontSize: 12.5, color: "var(--text)", padding: "4px 0 4px 16px",
                position: "relative",
              }}>
                <span style={{ position: "absolute", left: 0, color: "var(--muted)" }}>▸</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
