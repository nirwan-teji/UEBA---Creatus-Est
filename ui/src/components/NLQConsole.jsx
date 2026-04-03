import { Alert, Card, Form, Input, List, Skeleton, Space, Tag, Typography } from "antd";
import { useCallback, useState } from "react";
import { users } from "../data/mockData.js";
import { useAlerts } from "../context/AlertsContext.jsx";

const { Search } = Input;
const { Text } = Typography;

const NLQConsole = () => {
  const { alerts } = useAlerts();
  const [isLoading, setIsLoading] = useState(false);
  const [query, setQuery] = useState("Show all high-risk users");
  const [results, setResults] = useState({ intent: "", items: [] });
  const [error, setError] = useState(null);

  const runQuery = useCallback(
    async (value) => {
      const finalQuery = value || query;
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/nlq?query=${encodeURIComponent(finalQuery)}`);
        if (!response.ok) {
          throw new Error(`Backend responded with ${response.status}`);
        }
        const payload = await response.json();
        setResults({ intent: payload.intent, items: payload.results });
      } catch (err) {
        setError(err.message);
        const lowered = finalQuery.toLowerCase();
        const fallback = alerts.filter((item) =>
          [item.user, item.department, item.type, item.severity]
            .filter(Boolean)
            .some((field) => field.toLowerCase().includes(lowered))
        );
        const highRiskUsers = users.filter((user) => user.riskScore >= 70);
        setResults({
          intent: "fallback",
          items: fallback.length > 0 ? fallback : highRiskUsers
        });
      } finally {
        setIsLoading(false);
        setQuery(finalQuery);
      }
    },
    [query]
  );

  return (
    <Space direction="vertical" size={24} style={{ width: "100%" }}>
      <Card className="stat-card" title="Natural Language Query" bordered={false}>
        <Form layout="vertical" onFinish={({ prompt }) => runQuery(prompt)}>
          <Form.Item label="Ask a question" name="prompt" initialValue={query}>
            <Search
              enterButton="Query"
              size="large"
              placeholder="e.g. What happened in Finance department today?"
              onSearch={(value) => runQuery(value)}
              loading={isLoading}
            />
          </Form.Item>
        </Form>
        {error && (
          <Alert
            showIcon
            type="warning"
            message="Falling back to mock data"
            description={error}
            style={{ marginTop: 16 }}
          />
        )}
      </Card>

      <Card className="stat-card" title={`Intent: ${results.intent || "Pending"}`} bordered={false}>
        {isLoading ? (
          <Skeleton active paragraph={{ rows: 4 }} />
        ) : (
          <List
            dataSource={results.items}
            locale={{ emptyText: "Start with a query to see results." }}
            renderItem={(item, index) => (
              <List.Item>
                <List.Item.Meta
                  title={<Text strong>{item.user ?? item.type ?? `Result ${index + 1}`}</Text>}
                  description={
                    <Space size="small" wrap>
                      {Object.entries(item).map(([key, value]) => (
                        <Tag key={key} color="geekblue">
                          {key}: {String(value)}
                        </Tag>
                      ))}
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </Space>
  );
};

export default NLQConsole;
