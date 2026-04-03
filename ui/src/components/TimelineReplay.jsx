import { Card, List, Typography } from "antd";

const TimelineReplay = ({ events }) => (
  <Card className="stat-card" title="Incident Timeline Replay" bordered={false}>
    <List
      dataSource={events}
      renderItem={(event) => (
        <List.Item className="timeline-event">
          <List.Item.Meta
            title={<Typography.Text strong>{event.timestamp}</Typography.Text>}
            description={event.event}
          />
        </List.Item>
      )}
    />
  </Card>
);

export default TimelineReplay;
