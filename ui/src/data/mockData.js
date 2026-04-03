export const alerts = [
  {
    id: "ALRT-0001",
    user: "UZR-001",
    name: "Alex Johnson",
    department: "Engineering",
    type: "Suspicious File Activity",
    severity: "High",
    riskScore: 82,
    timestamp: "2025-11-28T02:23:15Z",
    explanations: [
      "Accessed unusual file location",
      "USB write detected",
      "Peer group activity 3.5x baseline"
    ]
  },
  {
    id: "ALRT-0002",
    user: "UZR-014",
    name: "Priya Das",
    department: "Finance",
    type: "Anomalous Logon Burst",
    severity: "Medium",
    riskScore: 64,
    timestamp: "2025-11-28T14:51:04Z",
    explanations: [
      "Login burst detected outside business hours",
      "New workstation observed"
    ]
  },
  {
    id: "ALRT-0003",
    user: "UZR-043",
    name: "Miguel Rivera",
    department: "Sales",
    type: "External Data Exfil",
    severity: "Critical",
    riskScore: 91,
    timestamp: "2025-11-27T21:12:44Z",
    explanations: [
      "ZIP attachment sent to external domain",
      "USB write 3 minutes prior"
    ]
  }
];

export const users = [
  {
    user: "UZR-001",
    name: "Alex Johnson",
    department: "Engineering",
    riskScore: 89,
    trend: "rising",
    peerDelta: "+245%",
    anomalyBreakdown: {
      logins: 21,
      files: 18,
      devices: 4,
      emails: 9
    }
  },
  {
    user: "UZR-014",
    name: "Priya Das",
    department: "Finance",
    riskScore: 61,
    trend: "steady",
    peerDelta: "+34%",
    anomalyBreakdown: {
      logins: 9,
      files: 4,
      devices: 1,
      emails: 6
    }
  },
  {
    user: "UZR-043",
    name: "Miguel Rivera",
    department: "Sales",
    riskScore: 48,
    trend: "declining",
    peerDelta: "-12%",
    anomalyBreakdown: {
      logins: 5,
      files: 3,
      devices: 0,
      emails: 1
    }
  }
];

export const anomaliesPerDay = [
  { date: "Nov 22", anomalies: 12 },
  { date: "Nov 23", anomalies: 9 },
  { date: "Nov 24", anomalies: 15 },
  { date: "Nov 25", anomalies: 11 },
  { date: "Nov 26", anomalies: 17 },
  { date: "Nov 27", anomalies: 19 },
  { date: "Nov 28", anomalies: 23 }
];

export const departmentHistogram = [
  { department: "Engineering", anomalies: 38 },
  { department: "Finance", anomalies: 21 },
  { department: "Sales", anomalies: 15 },
  { department: "HR", anomalies: 7 },
  { department: "Operations", anomalies: 10 }
];

export const peerComparison = [
  { label: "User", score: 89 },
  { label: "Team Avg", score: 54 },
  { label: "Org Avg", score: 42 }
];

export const timelineReplay = [
  { timestamp: "02:19:18", event: "Logon from PC-0414" },
  { timestamp: "02:21:30", event: "Opened sensitive file" },
  { timestamp: "02:22:10", event: "USB Write detected" },
  { timestamp: "02:23:15", event: "External email sent with attachment" }
];

export const userProfiles = {
  "UZR-001": {
    user: "UZR-001",
    name: "Alex Johnson",
    department: "Engineering",
    role: "Senior Developer",
    riskScore: 89,
    riskBreakdown: {
      mlScore: 52,
      ruleScore: 27,
      peerModifier: 10
    },
    authenticationHistory: [
      { timestamp: "02:19:18", event: "Logon from PC-0414" },
      { timestamp: "11:31:52", event: "VPN Login from home network" }
    ],
    fileTimeline: [
      { timestamp: "02:21:30", event: "Opened sensitive roadmap.pdf" },
      { timestamp: "15:45:10", event: "Modified project spec" }
    ],
    deviceUsage: [
      { timestamp: "02:22:10", event: "USB Write detected" },
      { timestamp: "09:41:21", event: "New external monitor" }
    ],
    emailActivity: [
      { timestamp: "02:23:15", event: "External email sent with attachment" },
      { timestamp: "16:05:44", event: "Internal update to ENG leads" }
    ],
    explanations: [
      "Combination of high-severity rule triggers",
      "IsolationForest score above dynamic threshold",
      "Peer comparison variance exceeds 3x"
    ],
    timeline: timelineReplay
  },
  "UZR-014": {
    user: "UZR-014",
    name: "Priya Das",
    department: "Finance",
    role: "Financial Analyst",
    riskScore: 61,
    riskBreakdown: {
      mlScore: 32,
      ruleScore: 21,
      peerModifier: 8
    },
    authenticationHistory: [
      { timestamp: "05:12:02", event: "Logon from PC-1203" },
      { timestamp: "21:51:04", event: "Login burst from remote desktop" }
    ],
    fileTimeline: [
      { timestamp: "21:52:55", event: "Opened payroll_export.csv" }
    ],
    deviceUsage: [{ timestamp: "21:48:45", event: "New thin client registered" }],
    emailActivity: [
      { timestamp: "21:54:12", event: "External email to vendor" }
    ],
    explanations: [
      "After-hours login burst",
      "Accessed finance export outside change window"
    ],
    timeline: [
      { timestamp: "21:48:45", event: "New thin client registered" },
      { timestamp: "21:51:04", event: "Login burst from remote desktop" },
      { timestamp: "21:52:55", event: "Opened payroll_export.csv" },
      { timestamp: "21:54:12", event: "External email to vendor" }
    ]
  }
};
