import { Segmented } from "antd";
import { useMode } from "../context/ModeContext.jsx";

const ModeToggle = () => {
  const { mode, setMode } = useMode();

  return (
    <Segmented
      value={mode}
      onChange={(value) => setMode(value)}
      options={[
        { label: "Analyst", value: "analyst" },
        { label: "Manager", value: "manager" }
      ]}
      className="ueba-mode-toggle"
    />
  );
};

export default ModeToggle;
