import { createContext, useContext, useMemo, useState } from "react";

const ModeContext = createContext();

export const ModeProvider = ({ children }) => {
  const [mode, setMode] = useState("analyst");

  const value = useMemo(
    () => ({
      mode,
      setMode
    }),
    [mode]
  );

  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
};

export const useMode = () => {
  const context = useContext(ModeContext);
  if (!context) {
    throw new Error("useMode must be used within ModeProvider");
  }
  return context;
};
