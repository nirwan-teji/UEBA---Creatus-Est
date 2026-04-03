import { Card, Col, Progress, Row, Space, Statistic, Tag } from "antd";
import { useMode } from "../context/ModeContext.jsx";
import { users } from "../data/mockData.js";

const trendStyles = {
  rising: { backgroundColor: "rgba(6, 68, 32, 0.15)", color: "#064420", borderColor: "#064420" },
  steady: { backgroundColor: "rgba(11, 110, 79, 0.15)", color: "#0b6e4f", borderColor: "#0b6e4f" },
  declining: { backgroundColor: "rgba(0, 0, 0, 0.15)", color: "#0b0f0c", borderColor: "#0b0f0c" }
};

const RiskSummaryCards = () => {
  const { mode } = useMode();

  return (
    <Row gutter={[16, 16]}>
      {users.map((user) => (
        <Col key={user.user} xs={24} sm={12} lg={8}>
          <Card className="stat-card" title={user.name} bordered={false}>
            <Space direction="vertical" size="small" style={{ width: "100%" }}>
              <Statistic
                title="Risk Score"
                value={user.riskScore}
                suffix="/ 100"
                valueStyle={{ color: "#064420" }}
              />
              <Tag style={{ ...trendStyles[user.trend], textTransform: "capitalize" }}>{user.trend}</Tag>
              <Progress
                percent={user.riskScore}
                showInfo={false}
                strokeColor={{ from: "#064420", to: "#0b6e4f" }}
              />
              {mode === "analyst" && (
                <Space direction="vertical" size={4}>
                  <div>Peer Delta: {user.peerDelta}</div>
                  <div>
                    Activity Mix: Logins {user.anomalyBreakdown.logins}, Files {""}
                    {user.anomalyBreakdown.files}, Devices {user.anomalyBreakdown.devices}, Emails {""}
                    {user.anomalyBreakdown.emails}
                  </div>
                </Space>
              )}
            </Space>
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default RiskSummaryCards;
