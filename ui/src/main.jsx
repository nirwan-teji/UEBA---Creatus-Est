import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { AlertsProvider } from "./context/AlertsContext.jsx";
import "antd/dist/reset.css";
import "./styles/main.scss";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AlertsProvider>
        <App />
      </AlertsProvider>
    </BrowserRouter>
  </React.StrictMode>
);
