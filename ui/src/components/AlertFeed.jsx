import { Alert, Avatar, Card, List, Space, Tag, Typography } from "antd";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { useMemo } from "react";
import { useAlerts } from "../context/AlertsContext.jsx";

dayjs.extend(relativeTime);

const severityColor = {
  High: "#064420",
  Medium: "#0b6e4f",
  Critical: "#03140a"
};

const AlertFeed = () => {
  const { alerts, isLoading, error } = useAlerts();
  const visibleAlerts = useMemo(() => alerts.slice(0, 8), [alerts]);

  return (
    <Card className="stat-card" title="Real-time Alert Feed" bordered={false}>
      {error && (
        <Alert
          type="warning"
          showIcon
          message="Unable to refresh alert feed"
          description={error}
          style={{ marginBottom: 16 }}
        />
      )}
      <List
        itemLayout="horizontal"
        dataSource={visibleAlerts}
        loading={isLoading}
        locale={{ emptyText: "No alerts available. Run the streaming job to generate alerts." }}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <Avatar style={{ backgroundColor: "#064420" }}>
                  {String(item.user).slice(-3).toUpperCase()}
                </Avatar>
              }
              title={
                <Space size="middle">
                  <Typography.Text strong>{item.type}</Typography.Text>
                  <Tag
                    style={{
                      backgroundColor: severityColor[item.severity] || "#0b6e4f",
                      color: "#ffffff",
                      borderColor: severityColor[item.severity] || "#0b6e4f"
                    }}
                  >
                    {item.severity}
                  </Tag>
                  <Typography.Text type="secondary" style={{ color: "#3a4a3f" }}>
                    Score {item.riskScore.toFixed(1)}
                  </Typography.Text>
                </Space>
              }
              description={
                <Space direction="vertical" size={4}>
                  <Typography.Text type="secondary" style={{ color: "#3a4a3f" }}>
                    {item.department} • {item.functionalUnit}
                    {item.timestamp && ` • ${dayjs(item.timestamp).fromNow()}`}
                  </Typography.Text>
                  <Typography.Text>{item.explanations[0]}</Typography.Text>
                </Space>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
};

export default AlertFeed;
