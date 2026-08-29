import { useState, useEffect, useCallback, useRef } from "react";
import StatCard from "./StatCard";
import ClassificationChart from "./ClassificationChart";
import ScanTester from "./ScanTester";
import ReportsTable from "./ReportsTable";
import LiveClock from "./LiveClock";

const API_BASE = "http://127.0.0.1:8000";
const POLL_INTERVAL_MS = 5000;

export default function AdminDashboard({ onLogout }) {
  const [stats, setStats] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const sessionStart = useRef(new Date());

  const loadData = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [statsRes, reportsRes] = await Promise.all([
        fetch(`${API_BASE}/statistics`),
        fetch(`${API_BASE}/reports`),
      ]);
      setStats(await statsRes.json());
      setReports(await reportsRes.json());
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      if (!silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(() => loadData(true), POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loadData]);

  if (loading) {
    return <div style={{ padding: 40, color: "var(--muted)" }} className="mono">Loading dashboard…</div>;
  }
  if (!stats) {
    return <div style={{ padding: 40, color: "var(--alert)" }} className="mono">Could not load data. Is the backend running?</div>;
  }

  return (
    <div style={{ padding: 28, maxWidth: 1200, margin: "0 auto" }}>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "flex-end",
        marginBottom: 24, flexWrap: "wrap", gap: 12,
      }}>
        <div>
          <div className="mono" style={{
            fontSize: 10, letterSpacing: "1px", textTransform: "uppercase",
            color: "var(--signal)", marginBottom: 6,
          }}>
            Hybrid Phishing Detector
          </div>
          <h1 style={{ margin: 0, fontSize: 26, fontWeight: 600 }}>Admin Console</h1>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <LiveClock startTime={sessionStart.current} />
          <button
            onClick={onLogout}
            className="mono"
            style={{
              background: "transparent", border: "1px solid var(--line)", color: "var(--muted)",
              borderRadius: 4, padding: "6px 12px", fontSize: 10, textTransform: "uppercase",
              cursor: "pointer",
            }}
          >
            Log out
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
        <StatCard label="Total Scans" value={stats.total_scans} />
        <StatCard label="Legitimate" value={stats.legitimate_count} accent="var(--signal)" />
        <StatCard label="Phishing" value={stats.phishing_count} accent="var(--alert)" />
        <StatCard label="Suspicious" value={stats.suspicious_count} accent="var(--warn)" />
        <StatCard label="Avg. Confidence" value={`${(stats.average_confidence * 100).toFixed(1)}%`} />
        <StatCard label="User Reports" value={stats.total_reports} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
        <ClassificationChart stats={stats} />
        <ScanTester onScanComplete={() => loadData(true)} />
      </div>

      <ReportsTable reports={reports} />
    </div>
  );
}
