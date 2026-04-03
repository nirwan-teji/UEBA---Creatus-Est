import { Alert, Button, Card, Space, Table, Tag, Typography } from "antd";
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useAlerts } from "../context/AlertsContext.jsx";

const severityStyles = {
  High: { backgroundColor: "#064420", color: "#ffffff", borderColor: "#064420" },
  Medium: { backgroundColor: "#0b6e4f", color: "#ffffff", borderColor: "#0b6e4f" },
  Critical: { backgroundColor: "#03140a", color: "#ffffff", borderColor: "#03140a" }
};

const AlertsTable = () => {
  const navigate = useNavigate();
  const { alerts, isLoading, error, refresh } = useAlerts();

  const dataSource = useMemo(
    () =>
      alerts.map((item) => ({
        ...item,
        key: item.id,
        riskScoreDisplay: item.riskScore.toFixed(1)
      })),
    [alerts]
  );

  const columns = [
    {
      title: "Alert ID",
      dataIndex: "id",
      key: "id"
    },
    {
      title: "User",
      dataIndex: "user",
      key: "user",
      render: (value, record) => (
        <Space direction="vertical" size={0}>
          <Typography.Text strong>{value}</Typography.Text>
          <Typography.Text type="secondary">{record.department}</Typography.Text>
        </Space>
      )
    },
    {
      title: "Department",
      dataIndex: "department",
      key: "department"
    },
    {
      title: "Type",
      dataIndex: "type",
      key: "type",
      render: (value) => value ?? "Risk Alert"
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      render: (value) => (
        <Tag style={{ ...(severityStyles[value] || severityStyles.High) }}>{value}</Tag>
      )
    },
    {
      title: "Risk Score",
      dataIndex: "riskScore",
      key: "riskScore",
      render: (_, record) => record.riskScoreDisplay
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => (
        <Button type="link" onClick={() => navigate(`/users/${record.user}`)}>
          View User
        </Button>
      )
    }
  ];

  return (
    <Card
      className="stat-card"
      title="Alerts"
      bordered={false}
      extra={<Button onClick={refresh}>Refresh</Button>}
    >
      {error && (
        <Alert
          type="warning"
          showIcon
          message="Unable to load alerts"
          description={error}
          style={{ marginBottom: 16 }}
        />
      )}
      <Table
        columns={columns}
        dataSource={dataSource}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 8 }}
      />
    </Card>
  );
};

export default AlertsTable;
