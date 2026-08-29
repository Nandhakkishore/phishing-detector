export default function StatCard({ label, value, accent, mono = true }) {
  return (
    <div style={{
      background: "var(--panel)",
      border: "1px solid var(--line)",
      borderLeft: `3px solid ${accent || "var(--line)"}`,
      borderRadius: 6,
      padding: "16px 18px",
      minWidth: 150,
      flex: "1 1 150px",
    }}>
      <div className={mono ? "mono" : ""} style={{
        fontSize: 26, fontWeight: 700, color: accent || "var(--text)",
      }}>
        {value}
      </div>
      <div className="mono" style={{
        fontSize: 10, letterSpacing: "0.8px", textTransform: "uppercase",
        color: "var(--muted)", marginTop: 6,
      }}>
        {label}
      </div>
    </div>
  );
}
