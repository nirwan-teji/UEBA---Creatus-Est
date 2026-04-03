import { Card } from "antd";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { departmentHistogram } from "../data/mockData.js";

const DepartmentHeatmap = () => (
  <Card className="stat-card" title="Department Anomaly Summary" bordered={false}>
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={departmentHistogram}>
        <XAxis dataKey="department" stroke="#0b0f0c" axisLine={false} tickLine={false} />
        <YAxis stroke="#0b0f0c" axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ background: "rgba(255, 255, 255, 0.98)", border: "1px solid #c8d5c0", color: "#0b0f0c" }}
        />
        <Bar dataKey="anomalies" fill="#0b6e4f" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  </Card>
);

export default DepartmentHeatmap;
