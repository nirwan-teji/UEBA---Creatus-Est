import { Layout, Menu, Space, Typography } from "antd";
import { AlertOutlined, DashboardOutlined, SearchOutlined, UserOutlined } from "@ant-design/icons";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import Dashboard from "./components/Dashboard.jsx";
import AlertsTable from "./components/AlertsTable.jsx";
import UserDetail from "./components/UserDetail.jsx";
import NLQConsole from "./components/NLQConsole.jsx";
import ModeToggle from "./components/ModeToggle.jsx";
import { ModeProvider, useMode } from "./context/ModeContext.jsx";

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

const navItems = [
  { key: "/dashboard", icon: <DashboardOutlined />, label: "Dashboard" },
  { key: "/alerts", icon: <AlertOutlined />, label: "Alerts" },
  { key: "/users/UZR-001", icon: <UserOutlined />, label: "User Detail" },
  { key: "/nlq", icon: <SearchOutlined />, label: "NL Query" }
];

const Shell = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { mode } = useMode();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        theme="dark"
        style={{ background: "#051b13" }}
      >
        <div style={{ padding: "24px", textAlign: "center" }}>
          <Title level={4} style={{ color: "#ffffff", marginBottom: 0 }}>
            UEBA Console
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          onClick={({ key }) => navigate(key)}
          items={navItems}
          style={{ background: "transparent" }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#ffffff",
            paddingInline: 32,
            borderBottom: "1px solid #c8d5c0"
          }}
        >
          <Space style={{ width: "100%", justifyContent: "space-between" }} align="center">
            <Title
              level={2}
              style={{
                color: "#03140a",
                margin: 0,
                fontFamily: '"Playfair Display", "Times New Roman", serif',
                letterSpacing: "0.08em",
                textTransform: "uppercase"
              }}
            >
              Insider Risk Operations Center
            </Title>
            <ModeToggle />
          </Space>
        </Header>
        <Content style={{ margin: "24px", minHeight: 280 }}>{children}</Content>
      </Layout>
    </Layout>
  );
};

const App = () => (
  <ModeProvider>
    <Shell>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/alerts" element={<AlertsTable />} />
        <Route path="/users/:userId" element={<UserDetail />} />
        <Route path="/nlq" element={<NLQConsole />} />
      </Routes>
    </Shell>
  </ModeProvider>
);

export default App;
