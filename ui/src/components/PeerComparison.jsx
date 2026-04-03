import { Card } from "antd";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { peerComparison } from "../data/mockData.js";

const PeerComparison = () => (
  <Card className="stat-card" title="Peer Group Comparison" bordered={false}>
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={peerComparison} layout="vertical">
        <XAxis type="number" domain={[0, 100]} hide />
        <YAxis type="category" dataKey="label" stroke="#0b0f0c" />
        <Tooltip
          contentStyle={{ background: "rgba(255, 255, 255, 0.98)", border: "1px solid #c8d5c0", color: "#0b0f0c" }}
        />
        <Bar dataKey="score" fill="#064420" radius={[0, 8, 8, 0]} />
      </BarChart>
    </ResponsiveContainer>
  </Card>
);

export default PeerComparison;
