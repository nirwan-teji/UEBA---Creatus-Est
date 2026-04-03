import { Col, Row } from "antd";
import AlertFeed from "./AlertFeed.jsx";
import DepartmentHeatmap from "./DepartmentHeatmap.jsx";
import PeerComparison from "./PeerComparison.jsx";
import RiskSummaryCards from "./RiskSummaryCards.jsx";
import RiskTrendChart from "./RiskTrendChart.jsx";

const Dashboard = () => (
  <Row gutter={[24, 24]}>
    <Col span={24}>
      <RiskSummaryCards />
    </Col>
    <Col xs={24} lg={14}>
      <RiskTrendChart />
    </Col>
    <Col xs={24} lg={10}>
      <PeerComparison />
    </Col>
    <Col xs={24} lg={13}>
      <DepartmentHeatmap />
    </Col>
    <Col xs={24} lg={11}>
      <AlertFeed />
    </Col>
  </Row>
);

export default Dashboard;
