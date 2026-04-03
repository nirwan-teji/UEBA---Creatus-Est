import { Alert, Card, Col, List, Progress, Row, Space, Statistic, Tag, Typography } from "antd";
import { useMemo } from "react";
import { useParams } from "react-router-dom";
import TimelineReplay from "./TimelineReplay.jsx";
import { useMode } from "../context/ModeContext.jsx";
import { useAlerts } from "../context/AlertsContext.jsx";
import { timelineReplay, userProfiles } from "../data/mockData.js";

const { Title, Text } = Typography;

const UserDetail = () => {
  const { userId } = useParams();
  const { mode } = useMode();
  const { alerts: liveAlerts } = useAlerts();

  const userAlerts = useMemo(
    () => liveAlerts.filter((alert) => alert.user === userId),
    [liveAlerts, userId]
  );

  const profile = useMemo(() => {
    if (userProfiles[userId]) {
      return userProfiles[userId];
    }
    if (userAlerts.length > 0) {
      const latest = userAlerts[0];
      return {
        user: latest.user,
        name: latest.user,
        department: latest.department ?? "Unknown",
        role: "N/A",
        riskScore: Number(latest.riskScore.toFixed(1)),
        riskBreakdown: { mlScore: 0, ruleScore: 0, peerModifier: 0 },
        authenticationHistory: [],
        fileTimeline: [],
        deviceUsage: [],
        emailActivity: [],
        explanations: latest.explanations ?? [],
        timeline: []
      };
    }
    return userProfiles["UZR-001"];
  }, [userId, userAlerts]);

  const profileSource = useMemo(() => {
    if (userProfiles[userId]) {
      return "mock";
    }
    if (userAlerts.length > 0) {
      return "live";
    }
    return "default";
  }, [userId, userAlerts]);

  return (
    <Space direction="vertical" size={24} style={{ width: "100%" }}>
      {profileSource === "live" && (
        <Alert
          type="info"
          showIcon
          message="Live profile"
          description="This user does not have enriched metadata yet. Showing details derived from the latest alerts."
        />
      )}
      {profileSource === "default" && (
        <Alert
          type="warning"
          showIcon
          message="Using fallback profile"
          description="No live alerts available for this user. Displaying template profile data."
        />
      )}

      <Card className="stat-card" bordered={false}>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={12} lg={6}>
            <Statistic title="Current Risk Score" value={profile.riskScore} valueStyle={{ color: "#064420" }} />
          </Col>
          <Col xs={24} md={12} lg={6}>
            <Statistic title="Alerts" value={userAlerts.length} />
          </Col>
          <Col xs={24} md={12} lg={6}>
            <Statistic title="Department" value={profile.department} />
          </Col>
          <Col xs={24} md={12} lg={6}>
            <Statistic title="Role" value={profile.role} />
          </Col>
        </Row>
        <Row gutter={[24, 24]} style={{ marginTop: 16 }}>
          <Col xs={24} md={8}>
            <Title level={5}>ML Score</Title>
            <Progress percent={profile.riskBreakdown.mlScore} strokeColor="#0b6e4f" />
          </Col>
          <Col xs={24} md={8}>
            <Title level={5}>Rule Score</Title>
            <Progress percent={profile.riskBreakdown.ruleScore} strokeColor="#064420" />
          </Col>
          <Col xs={24} md={8}>
            <Title level={5}>Peer Modifier</Title>
            <Progress percent={profile.riskBreakdown.peerModifier} strokeColor="#052f1f" />
          </Col>
        </Row>
      </Card>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card className="stat-card" title="Authentication Timeline" bordered={false}>
            <List
              dataSource={profile.authenticationHistory}
              renderItem={(event) => (
                <List.Item>
                  <List.Item.Meta title={event.timestamp} description={event.event} />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card className="stat-card" title="File Activity" bordered={false}>
            <List
              dataSource={profile.fileTimeline}
              renderItem={(event) => (
                <List.Item>
                  <List.Item.Meta title={event.timestamp} description={event.event} />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card className="stat-card" title="Device Usage" bordered={false}>
            <List
              dataSource={profile.deviceUsage}
              renderItem={(event) => (
                <List.Item>
                  <List.Item.Meta title={event.timestamp} description={event.event} />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card className="stat-card" title="Email Activity" bordered={false}>
            <List
              dataSource={profile.emailActivity}
              renderItem={(event) => (
                <List.Item>
                  <List.Item.Meta title={event.timestamp} description={event.event} />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      <TimelineReplay events={profile.timeline ?? timelineReplay} />

      <Card className="stat-card" title="Explainability" bordered={false}>
        <Space direction="vertical" size={12}>
          {profile.explanations.map((reason) => (
            <Tag
              key={reason}
              style={{
                backgroundColor: "rgba(6, 68, 32, 0.12)",
                color: "#064420",
                borderColor: "#064420"
              }}
            >
              {reason}
            </Tag>
          ))}
        </Space>
      </Card>

      {mode === "analyst" && (
        <Card className="stat-card" title="Recent Alerts" bordered={false}>
          <List
            dataSource={userAlerts}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong>{item.type}</Text>
                      <Tag
                        style={{
                          backgroundColor: "#064420",
                          color: "#ffffff",
                          borderColor: "#064420"
                        }}
                      >
                        {item.severity}
                      </Tag>
                    </Space>
                  }
                  description={item.explanations.join(" • ")}
                />
              </List.Item>
            )}
          />
          <Alert
            type="info"
            showIcon
            message="Analyst Mode"
            description="Full alert trail is visible. Switch to Manager mode for high-level summaries."
            style={{ marginTop: 16 }}
          />
        </Card>
      )}
    </Space>
  );
};

export default UserDetail;
