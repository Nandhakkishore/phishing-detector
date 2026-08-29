import { useState, useEffect } from "react";

export default function LiveClock({ startTime }) {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const elapsedMs = now - startTime;
  const totalSeconds = Math.floor(elapsedMs / 1000);
  const hrs = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
  const mins = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const secs = String(totalSeconds % 60).padStart(2, "0");

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span style={{
        width: 7, height: 7, borderRadius: "50%",
        background: "var(--signal)",
        boxShadow: "0 0 6px var(--signal)",
        animation: "pulse 1.6s ease-in-out infinite",
        display: "inline-block",
      }} />
      <span className="mono" style={{ fontSize: 11, color: "var(--muted)" }}>
        {now.toLocaleTimeString()} · session {hrs}:{mins}:{secs}
      </span>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.35; }
        }
      `}</style>
    </div>
  );
}
