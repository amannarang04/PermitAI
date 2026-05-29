import React, { useState, useEffect } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, LineChart, Line, CartesianGrid } from "recharts";
import { BarChart2, Settings, Shield, RefreshCw, Save } from "lucide-react";
import axios from "axios";

interface AdminPortalProps {
  token: string;
  apiBaseUrl: string;
}

export const AdminPortal: React.FC<AdminPortalProps> = ({ token, apiBaseUrl }) => {
  const [activeTab, setActiveTab] = useState<"metrics" | "config" | "audit">("metrics");
  
  // Metrics States
  const [metricsData, setMetricsData] = useState<any>(null);
  const [queueStatus, setQueueStatus] = useState<any[]>([]);
  const [bottlenecks, setBottlenecks] = useState<any[]>([]);
  const [trends, setTrends] = useState<any[]>([]);
  const [metricsLoading, setMetricsLoading] = useState(false);

  // Config States
  const [configs, setConfigs] = useState<any[]>([]);
  const [configLoading, setConfigLoading] = useState(false);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editingValue, setEditingValue] = useState("");

  // Audit Logs States
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);

  useEffect(() => {
    if (activeTab === "metrics") fetchMetrics();
    else if (activeTab === "config") fetchConfigs();
    else if (activeTab === "audit") fetchAuditLogs();
  }, [activeTab]);

  const fetchMetrics = async () => {
    setMetricsLoading(true);
    try {
      const authHeader = { headers: { Authorization: `Bearer ${token}` } };
      
      const dashboardRes = await axios.get(`${apiBaseUrl}/api/admin/metrics/dashboard`, authHeader);
      setMetricsData(dashboardRes.data);

      const qsRes = await axios.get(`${apiBaseUrl}/api/admin/metrics/queue-status`, authHeader);
      setQueueStatus(qsRes.data);

      const bnRes = await axios.get(`${apiBaseUrl}/api/admin/metrics/bottleneck-analysis`, authHeader);
      setBottlenecks(bnRes.data);

      const trendsRes = await axios.get(`${apiBaseUrl}/api/admin/metrics/trends?days=7`, authHeader);
      setTrends(trendsRes.data.trends || []);
    } catch (err) {
      console.error(err);
    } finally {
      setMetricsLoading(false);
    }
  };

  const fetchConfigs = async () => {
    setConfigLoading(true);
    try {
      const res = await axios.get(`${apiBaseUrl}/api/admin/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfigs(res.data);
    } catch (err) {}
    finally { setConfigLoading(false); }
  };

  const fetchAuditLogs = async () => {
    setAuditLoading(true);
    try {
      const res = await axios.get(`${apiBaseUrl}/api/admin/audit-log`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAuditLogs(res.data.logs || []);
    } catch (err) {}
    finally { setAuditLoading(false); }
  };

  const handleUpdateConfig = async (key: string) => {
    try {
      await axios.put(`${apiBaseUrl}/api/admin/config/${key}`, {
        value: editingValue
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEditingKey(null);
      fetchConfigs();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to update configuration.");
    }
  };

  return (
    <div style={{ display: "flex", gap: "28px", maxWidth: "1200px", margin: "40px auto", padding: "0 24px" }} className="animate-fade-in">
      
      {/* Side Menu Tab Navigator */}
      <div style={{ width: "240px", display: "flex", flexDirection: "column", gap: "8px" }}>
        <button
          onClick={() => setActiveTab("metrics")}
          className="premium-btn"
          style={{
            justifyContent: "flex-start",
            background: activeTab === "metrics" ? "var(--primary-glow)" : "transparent",
            border: `1px solid ${activeTab === "metrics" ? "var(--primary-light)" : "transparent"}`,
            color: activeTab === "metrics" ? "#fff" : "var(--text-muted)",
            width: "100%"
          }}
        >
          <BarChart2 size={18} />
          <span>Operational Metrics</span>
        </button>
        <button
          onClick={() => setActiveTab("config")}
          className="premium-btn"
          style={{
            justifyContent: "flex-start",
            background: activeTab === "config" ? "var(--primary-glow)" : "transparent",
            border: `1px solid ${activeTab === "config" ? "var(--primary-light)" : "transparent"}`,
            color: activeTab === "config" ? "#fff" : "var(--text-muted)",
            width: "100%"
          }}
        >
          <Settings size={18} />
          <span>System Settings</span>
        </button>
        <button
          onClick={() => setActiveTab("audit")}
          className="premium-btn"
          style={{
            justifyContent: "flex-start",
            background: activeTab === "audit" ? "var(--primary-glow)" : "transparent",
            border: `1px solid ${activeTab === "audit" ? "var(--primary-light)" : "transparent"}`,
            color: activeTab === "audit" ? "#fff" : "var(--text-muted)",
            width: "100%"
          }}
        >
          <Shield size={18} />
          <span>Compliance Audit Trail</span>
        </button>
      </div>

      {/* Main Panel Content */}
      <div style={{ flex: 1 }}>
        
        {activeTab === "metrics" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.5rem" }}>System Performance Monitor</h3>
              <button onClick={fetchMetrics} className="premium-btn premium-btn-secondary" style={{ padding: "8px" }}>
                <RefreshCw size={16} />
              </button>
            </div>

            {metricsLoading ? (
              <div className="glass-card" style={{ padding: "60px", textAlign: "center" }}><p>Loading metrics data...</p></div>
            ) : (
              <>
                {/* Stats grid summary */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px" }}>
                  <div className="glass-card" style={{ background: "rgba(79, 70, 229, 0.05)" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>ACTIVE QUEUE BACKLOG</div>
                    <h2 style={{ fontSize: "2rem", marginTop: "4px" }}>{metricsData?.total_pending_applications || 0}</h2>
                  </div>
                  <div className="glass-card" style={{ background: "rgba(16, 185, 129, 0.05)" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>TOTAL APPROVALS</div>
                    <h2 style={{ fontSize: "2rem", marginTop: "4px" }}>{metricsData?.total_approved_applications || 0}</h2>
                  </div>
                  <div className="glass-card" style={{ background: "rgba(239, 68, 68, 0.05)" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>TOTAL REJECTIONS</div>
                    <h2 style={{ fontSize: "2rem", marginTop: "4px" }}>{metricsData?.total_rejected_applications || 0}</h2>
                  </div>
                </div>

                {/* Charts section */}
                <div className="premium-grid">
                  
                  {/* Queue Load Bar Chart */}
                  <div className="glass-card" style={{ height: "350px", display: "flex", flexDirection: "column" }}>
                    <h4 style={{ fontFamily: "var(--font-title)", marginBottom: "16px" }}>Pending Tasks Per Queue</h4>
                    <div style={{ flex: 1 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={queueStatus}>
                          <XAxis dataKey="queue_name" tick={{ fill: "#9ca3af", fontSize: 10 }} />
                          <YAxis tick={{ fill: "#9ca3af" }} />
                          <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid var(--border-color)" }} />
                          <Bar dataKey="pending_count" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Submission Trends Line Chart */}
                  <div className="glass-card" style={{ height: "350px", display: "flex", flexDirection: "column" }}>
                    <h4 style={{ fontFamily: "var(--font-title)", marginBottom: "16px" }}>7-Day Submission trends</h4>
                    <div style={{ flex: 1 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={trends}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="date" tick={{ fill: "#9ca3af", fontSize: 10 }} />
                          <YAxis tick={{ fill: "#9ca3af" }} />
                          <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid var(--border-color)" }} />
                          <Legend />
                          <Line type="monotone" dataKey="received" stroke="var(--primary-light)" strokeWidth={2} />
                          <Line type="monotone" dataKey="approved" stroke="var(--success)" strokeWidth={2} />
                          <Line type="monotone" dataKey="rejected" stroke="var(--danger)" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                </div>

                {/* Queue bottleneck tables */}
                <div className="glass-card">
                  <h4 style={{ fontFamily: "var(--font-title)", marginBottom: "16px" }}>Process Delay & Bottleneck Diagnostics</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {bottlenecks.map((b, idx) => (
                      <div key={idx} style={{
                        padding: "16px",
                        background: "rgba(255,255,255,0.01)",
                        border: "1px solid var(--border-color)",
                        borderRadius: "8px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                      }}>
                        <div>
                          <p style={{ fontWeight: 600, fontSize: "0.9rem" }}>Queue: {b.queue_name}</p>
                          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "2px" }}>Recommendation: {b.recommendation}</p>
                        </div>
                        <span style={{
                          padding: "4px 10px",
                          borderRadius: "4px",
                          fontSize: "0.75rem",
                          fontWeight: 700,
                          background: b.severity === "high" ? "rgba(239, 68, 68, 0.2)" : "rgba(245, 158, 11, 0.2)",
                          color: b.severity === "high" ? "#f87171" : "#fbbf24"
                        }}>{b.severity.toUpperCase()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === "config" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.5rem" }}>System Governance Configuration</h3>
            
            {configLoading ? (
              <div className="glass-card" style={{ padding: "60px", textAlign: "center" }}><p>Loading dynamic settings...</p></div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {configs.map((cfg) => (
                  <div key={cfg.key} className="glass-card" style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "16px"
                  }}>
                    <div style={{ maxWidth: "60%" }}>
                      <p style={{ fontWeight: 700, fontSize: "0.95rem", color: "var(--primary-light)" }}>{cfg.key}</p>
                      <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "2px" }}>{cfg.description}</p>
                    </div>

                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      {editingKey === cfg.key ? (
                        <>
                          <input 
                            type="text"
                            value={editingValue}
                            onChange={(e) => setEditingValue(e.target.value)}
                            className="premium-input"
                            style={{ width: "120px", padding: "6px 12px" }}
                          />
                          <button onClick={() => handleUpdateConfig(cfg.key)} className="premium-btn premium-btn-success" style={{ padding: "8px" }}>
                            <Save size={16} />
                          </button>
                        </>
                      ) : (
                        <>
                          <span style={{ background: "rgba(255,255,255,0.05)", padding: "6px 12px", borderRadius: "6px", fontSize: "0.85rem", border: "1px solid var(--border-color)", fontWeight: 700 }}>
                            {cfg.value}
                          </span>
                          <button onClick={() => { setEditingKey(cfg.key); setEditingValue(cfg.value); }} className="premium-btn premium-btn-secondary" style={{ padding: "6px 12px", fontSize: "0.8rem" }}>
                            Edit
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "audit" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.5rem" }}>Compliance Audit Logging</h3>
            
            {auditLoading ? (
              <div className="glass-card" style={{ padding: "60px", textAlign: "center" }}><p>Loading compliance logs...</p></div>
            ) : (
              <div style={{
                maxHeight: "600px",
                overflowY: "auto",
                border: "1px solid var(--border-color)",
                borderRadius: "12px",
                overflowX: "auto"
              }}>
                <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
                  <thead>
                    <tr style={{ background: "rgba(255,255,255,0.03)", borderBottom: "1px solid var(--border-color)", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                      <th style={{ padding: "12px 16px" }}>Timestamp</th>
                      <th style={{ padding: "12px 16px" }}>User</th>
                      <th style={{ padding: "12px 16px" }}>Action</th>
                      <th style={{ padding: "12px 16px" }}>Category</th>
                      <th style={{ padding: "12px 16px" }}>Details</th>
                    </tr>
                  </thead>
                  <tbody style={{ fontSize: "0.8rem" }}>
                    {auditLogs.map((log) => (
                      <tr key={log.id} style={{ borderBottom: "1px solid var(--border-color)", background: "rgba(255,255,255,0.005)" }}>
                        <td style={{ padding: "12px 16px", color: "var(--text-muted)" }}>{new Date(log.timestamp).toLocaleString()}</td>
                        <td style={{ padding: "12px 16px" }}>{log.username || `ID: ${log.user_id}`}</td>
                        <td style={{ padding: "12px 16px", fontWeight: 700 }}>{log.action.toUpperCase()}</td>
                        <td style={{ padding: "12px 16px" }}>
                          <span style={{
                            padding: "2px 6px",
                            borderRadius: "4px",
                            background: log.action_category === "write" ? "rgba(249, 115, 22, 0.15)" : "rgba(16, 185, 129, 0.15)",
                            color: log.action_category === "write" ? "#fb923c" : "#34d399",
                            fontSize: "0.7rem",
                            fontWeight: 700
                          }}>{log.action_category}</span>
                        </td>
                        <td style={{ padding: "12px 16px", color: "var(--text-muted)" }}>
                          {log.details ? JSON.stringify(log.details) : "No annotations"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

      </div>

    </div>
  );
};
