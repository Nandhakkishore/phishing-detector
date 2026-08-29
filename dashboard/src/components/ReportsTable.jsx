import { useState, useMemo } from "react";

const FILTERS = ["all", "legitimate", "phishing", "suspicious"];

export default function ReportsTable({ reports }) {
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    return reports.filter((r) => {
      const matchesFilter = filter === "all" || r.original_classification === filter;
      const matchesSearch = r.url.toLowerCase().includes(search.toLowerCase());
      return matchesFilter && matchesSearch;
    });
  }, [reports, filter, search]);

  return (
    <div style={{
      background: "var(--panel)", border: "1px solid var(--line)",
      borderRadius: 6, padding: 20,
    }}>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        flexWrap: "wrap", gap: 10, marginBottom: 14,
      }}>
        <div className="mono" style={{
          fontSize: 10, letterSpacing: "0.8px", textTransform: "uppercase",
          color: "var(--muted)",
        }}>
          User Reports ({filtered.length})
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            placeholder="Search URL…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: "var(--ink)", border: "1px solid var(--line)",
              borderRadius: 4, padding: "6px 10px", color: "var(--text)",
              fontSize: 12, outline: "none", width: 160,
            }}
          />
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className="mono"
              style={{
                background: filter === f ? "var(--line)" : "transparent",
                color: filter === f ? "var(--text)" : "var(--muted)",
                border: "1px solid var(--line)", borderRadius: 4,
                padding: "5px 10px", fontSize: 10.5, textTransform: "uppercase",
                cursor: "pointer", letterSpacing: "0.4px",
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div style={{
          textAlign: "center", padding: "32px 0", color: "var(--muted)", fontSize: 13,
        }}>
          No reports match this view.
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {["URL", "Original Classification", "Comment", "Time"].map((h) => (
                <th key={h} className="mono" style={{
                  textAlign: "left", padding: "8px 10px", fontSize: 10,
                  letterSpacing: "0.5px", textTransform: "uppercase",
                  color: "var(--muted)", borderBottom: "1px solid var(--line)",
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} style={{ borderBottom: "1px solid var(--line)" }}>
                <td className="mono" style={{ padding: "10px", fontSize: 12, wordBreak: "break-all" }}>{r.url}</td>
                <td style={{ padding: "10px", fontSize: 12.5, textTransform: "capitalize" }}>{r.original_classification}</td>
                <td style={{ padding: "10px", fontSize: 12.5, color: "var(--muted)" }}>{r.user_comment || "—"}</td>
                <td className="mono" style={{ padding: "10px", fontSize: 11, color: "var(--muted)" }}>
                  {new Date(r.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
