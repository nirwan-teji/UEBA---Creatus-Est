import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

const AlertsContext = createContext();

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const formatNumber = (value) => {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) ? numeric : 0;
};

const normaliseSeverity = (value) => {
  if (!value) return "Medium";
  const lowered = String(value).trim().toLowerCase();
  return lowered.charAt(0).toUpperCase() + lowered.slice(1);
};

const summariseMetrics = (metrics) => {
  const logons = formatNumber(metrics?.logon_total_events);
  const fileWrites = formatNumber(metrics?.file_write_events);
  const removable = formatNumber(metrics?.file_to_removable_events);
  const httpDomains = formatNumber(metrics?.http_unique_domain_count);
  const emailEvents = formatNumber(metrics?.email_total_events);

  const lines = [];
  lines.push(`${logons} logon events • ${fileWrites} file writes`);
  lines.push(`${removable} removable media actions • ${httpDomains} web domains`);
  lines.push(`${emailEvents} email events recorded`);
  return lines;
};

const transformAlert = (payload) => {
  const riskScore = Number(payload.risk_score ?? payload.riskScore ?? 0);
  const anomalyScore = Number(payload.anomaly_score ?? payload.anomalyScore ?? 0);
  const eventDate = payload.event_date || payload.eventDate || null;
  const metrics = payload.metrics ?? {};

  return {
    id: payload.id,
    user: payload.user,
    department: payload.department || "Unknown",
    functionalUnit: payload.functional_unit || payload.functionalUnit || "-",
    severity: normaliseSeverity(payload.severity),
    riskScore,
    anomalyScore,
    eventDate,
    timestamp: eventDate || null,
    type: "Risk Alert",
    metrics,
    explanations: [
      `Risk score ${riskScore.toFixed(1)} with anomaly score ${anomalyScore.toFixed(3)}`,
      ...summariseMetrics(metrics)
    ]
  };
};

export const AlertsProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [meta, setMeta] = useState(null);

  const fetchAlerts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/alerts`);
      if (!response.ok) {
        throw new Error(`Alert API responded with ${response.status}`);
      }
      const payload = await response.json();
      const transformed = Array.isArray(payload.alerts)
        ? payload.alerts.map(transformAlert)
        : [];
      setAlerts(transformed);
      setMeta(payload.meta ?? null);
    } catch (err) {
      setError(err.message ?? "Unable to load alerts");
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const contextValue = useMemo(
    () => ({ alerts, isLoading, error, meta, refresh: fetchAlerts }),
    [alerts, isLoading, error, meta, fetchAlerts]
  );

  return <AlertsContext.Provider value={contextValue}>{children}</AlertsContext.Provider>;
};

export const useAlerts = () => {
  const context = useContext(AlertsContext);
  if (!context) {
    throw new Error("useAlerts must be used within AlertsProvider");
  }
  return context;
};
