import { Card } from "antd";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { anomaliesPerDay } from "../data/mockData.js";

const RiskTrendChart = () => (
  <Card className="stat-card" title="Anomalies per Day" bordered={false}>
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={anomaliesPerDay}>
        <XAxis dataKey="date" stroke="#0b0f0c" tickLine={false} axisLine={false} />
        <YAxis stroke="#0b0f0c" tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ background: "rgba(255, 255, 255, 0.98)", border: "1px solid #c8d5c0", color: "#0b0f0c" }}
        />
        <Line type="monotone" dataKey="anomalies" stroke="#064420" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  </Card>
);

export default RiskTrendChart;
