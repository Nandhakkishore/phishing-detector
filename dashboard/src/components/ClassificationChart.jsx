import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function ClassificationChart({ stats }) {
  const data = {
    labels: ["Legitimate", "Phishing", "Suspicious"],
    datasets: [{
      data: [stats.legitimate_count, stats.phishing_count, stats.suspicious_count],
      backgroundColor: ["#2DD4BF", "#FF5470", "#FFB84D"],
      borderColor: "#131922",
      borderWidth: 3,
    }],
  };

  const options = {
    plugins: {
      legend: {
        position: "bottom",
        labels: { color: "#E8EDF2", font: { family: "Inter", size: 12 }, padding: 16 },
      },
    },
    cutout: "68%",
  };

  return (
    <div style={{
      background: "var(--panel)", border: "1px solid var(--line)",
      borderRadius: 6, padding: 20, height: "100%",
    }}>
      <div className="mono" style={{
        fontSize: 10, letterSpacing: "0.8px", textTransform: "uppercase",
        color: "var(--muted)", marginBottom: 14,
      }}>
        Classification Breakdown
      </div>
      <Doughnut data={data} options={options} />
    </div>
  );
}
