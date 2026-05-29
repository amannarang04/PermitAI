import React, { useState, useEffect } from "react";
import { Upload, Search, Calendar, Download, CheckCircle, ArrowRight } from "lucide-react";
import axios from "axios";

interface CitizenPortalProps {
  token: string;
  user: any;
  apiBaseUrl: string;
}

export const CitizenPortal: React.FC<CitizenPortalProps> = ({ token, user, apiBaseUrl }) => {
  const [activeTab, setActiveTab] = useState<"dashboard" | "upload" | "track" | "notifications">("dashboard");

  // Notifications
  const [notifications, setNotifications] = useState<any[]>([]);
  const [notifPreferences, setNotifPreferences] = useState({ email: true, sms: false, in_app: true });

  // Upload Form
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(false);
  const [uploadSuccessInfo, setUploadSuccessInfo] = useState<any>(null);
  const [uploadError, setUploadError] = useState("");


  // Tracking
  const [trackingId, setTrackingId] = useState("");
  const [trackingResult, setTrackingResult] = useState<any>(null);
  const [trackingError, setTrackingError] = useState("");
  const [trackingLoading, setTrackingLoading] = useState(false);

  // Load notifications & preferences
  useEffect(() => {
    fetchNotifications();
    fetchPreferences();
  }, [activeTab]);

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(`${apiBaseUrl}/api/notifications`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(res.data);
    } catch (err) {}
  };

  const fetchPreferences = async () => {
    // Current user endpoints contain pref
    try {
      const res = await axios.get(`${apiBaseUrl}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.data.notification_preferences) {
        setNotifPreferences(res.data.notification_preferences);
      }
    } catch (err) {}
  };

  const handleUpdatePreferences = async (updated: typeof notifPreferences) => {
    try {
      await axios.patch(`${apiBaseUrl}/api/notifications/preferences`, updated, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifPreferences(updated);
    } catch (err) {}
  };

  const handleMarkNotifRead = async (id: number) => {
    try {
      await axios.patch(`${apiBaseUrl}/api/notifications/${id}/read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchNotifications();
    } catch (err) {}
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError("Please select a file to upload.");
      return;
    }
    setUploadProgress(true);
    setUploadError("");
    setUploadSuccessInfo(null);

    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const res = await axios.post(`${apiBaseUrl}/api/applications/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });
      setUploadSuccessInfo(res.data);
      // Automatically fill the tracker with new ID
      setTrackingId(res.data.application_id);
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Upload failed. Verify file size and format.");
    } finally {
      setUploadProgress(false);
    }
  };

  const handleTrackApplication = async (appId: string) => {
    if (!appId.trim()) return;
    setTrackingLoading(true);
    setTrackingError("");
    setTrackingResult(null);

    try {
      const res = await axios.get(`${apiBaseUrl}/api/applications/track/${appId.trim()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTrackingResult(res.data);
    } catch (err: any) {
      setTrackingError(err.response?.data?.detail || "Application not found.");
    } finally {
      setTrackingLoading(false);
    }
  };

  const handleDownloadCertificate = async (appId: string) => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/applications/${appId}/download-permit`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: "blob"
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `permit_${appId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      alert("Failed to download certificate. Verify if the application is approved.");
    }
  };

  return (
    <div style={{ display: "flex", gap: "32px", maxWidth: "1200px", margin: "40px auto", padding: "0 24px" }} className="animate-fade-in">
      
      {/* Side Menu Tab Navigator */}
      <div style={{ width: "240px", display: "flex", flexDirection: "column", gap: "8px" }}>
        <button
          onClick={() => setActiveTab("dashboard")}
          className="premium-btn"
          style={{
            justifyContent: "flex-start",
            background: activeTab === "dashboard" ? "var(--primary-glow)" : "transparent",
            border: `1px solid ${activeTab === "dashboard" ? "var(--primary-light)" : "transparent"}`,
            color: activeTab === "dashboard" ? "#fff" : "var(--text-muted)",
            width: "100%"
          }}
        >
          📂 Application Dashboard
        </button>
        <button
          onClick={() => setActiveTab("upload")}
          className="premium-btn"
          style={{
            justifyContent: "flex-start",
            background: activeTab === "upload" ? "var(--primary-glow)" : "transparent",
            border: `1px solid ${activeTab === "upload" ? "var(--primary-light)" : "transparent"}`,
            color: activeTab === "upload" ? "#fff" : "var(--text-muted)",
            width: "100%"
          }}
        >
          📤 Upload New Permit Form
        </button>
        <button
          onClick={() => setActiveTab("track")}
          className="premium-btn"
          style={{
            justifyContent: "flex-start",
            background: activeTab === "track" ? "var(--primary-glow)" : "transparent",
            border: `1px solid ${activeTab === "track" ? "var(--primary-light)" : "transparent"}`,
            color: activeTab === "track" ? "#fff" : "var(--text-muted)",
            width: "100%"
          }}
        >
          🔍 Track & Verify Permit
        </button>
        <button
          onClick={() => setActiveTab("notifications")}
          className="premium-btn"
          style={{
            justifyContent: "flex-start",
            background: activeTab === "notifications" ? "var(--primary-glow)" : "transparent",
            border: `1px solid ${activeTab === "notifications" ? "var(--primary-light)" : "transparent"}`,
            color: activeTab === "notifications" ? "#fff" : "var(--text-muted)",
            width: "100%"
          }}
        >
          ⚙️ Settings & Preferences
        </button>
      </div>

      {/* Main Panel Content */}
      <div style={{ flex: 1 }}>
        
        {activeTab === "dashboard" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <div className="glass-card" style={{ background: "linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(17, 24, 39, 0.7) 100%)" }}>
              <h2 style={{ fontFamily: "var(--font-title)", fontSize: "1.8rem", marginBottom: "8px" }}>
                Welcome, {user.full_name || user.username} 👋
              </h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
                Submit details to create new building projects, verify compliance status, or download approved official permit certificates.
              </p>
            </div>

            <div className="premium-grid">
              
              <div className="glass-card" style={{ textAlign: "center", cursor: "pointer" }} onClick={() => setActiveTab("upload")}>
                <div style={{ fontSize: "2rem", marginBottom: "12px" }}>📂</div>
                <h4 style={{ fontFamily: "var(--font-title)", marginBottom: "8px" }}>File Application</h4>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Submit scanned PDF or images of building permit forms.</p>
              </div>

              <div className="glass-card" style={{ textAlign: "center", cursor: "pointer" }} onClick={() => setActiveTab("track")}>
                <div style={{ fontSize: "2rem", marginBottom: "12px" }}>🔍</div>
                <h4 style={{ fontFamily: "var(--font-title)", marginBottom: "8px" }}>Track Real-time</h4>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Monitor compliance flags, queue checks, and reviews.</p>
              </div>

            </div>
          </div>
        )}

        {activeTab === "upload" && (
          <div className="glass-card">
            <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.4rem", marginBottom: "8px" }}>Upload Permit Application</h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "24px" }}>
              Upload a building permit PDF, JPEG, or PNG form. Max file size limit is 10MB.
            </p>

            {uploadError && (
              <div style={{ background: "rgba(239, 68, 68, 0.15)", border: "1px solid var(--danger)", borderRadius: "8px", padding: "12px 16px", color: "#f87171", marginBottom: "20px", fontSize: "0.85rem" }}>
                {uploadError}
              </div>
            )}

            {uploadSuccessInfo ? (
              <div style={{ background: "rgba(16, 185, 129, 0.15)", border: "1px solid var(--success)", borderRadius: "12px", padding: "24px", color: "#fff", display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <CheckCircle size={28} color="var(--success)" />
                  <div>
                    <h4 style={{ fontFamily: "var(--font-title)", color: "var(--success)" }}>Form Uploaded Successfully!</h4>
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>The compliance parser has initiated background extraction checks.</span>
                  </div>
                </div>
                
                <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: "8px", padding: "16px", border: "1px solid var(--border-color)" }}>
                  <div style={{ fontSize: "0.85rem", marginBottom: "6px" }}>Application ID: <b style={{ color: "var(--secondary)", letterSpacing: "0.05em" }}>{uploadSuccessInfo.application_id}</b></div>
                  <div style={{ fontSize: "0.85rem", marginBottom: "6px" }}>Current Status: <span className={`status-badge status-${uploadSuccessInfo.status}`}>{uploadSuccessInfo.status}</span></div>
                  <div style={{ fontSize: "0.85rem" }}>Message: <span style={{ color: "var(--text-muted)" }}>{uploadSuccessInfo.message}</span></div>
                </div>

                <button 
                  onClick={() => { setActiveTab("track"); handleTrackApplication(uploadSuccessInfo.application_id); }}
                  className="premium-btn premium-btn-primary"
                  style={{ width: "fit-content" }}
                >
                  <span>Track Evaluation Live</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            ) : (
              <form onSubmit={handleFileUpload} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                
                {/* Drag Drop File Zone */}
                <div style={{
                  border: "2px dashed var(--border-color)",
                  borderRadius: "12px",
                  padding: "40px 20px",
                  textAlign: "center",
                  background: uploadFile ? "rgba(79, 70, 229, 0.05)" : "transparent",
                  cursor: "pointer",
                  borderColor: uploadFile ? "var(--primary-light)" : "var(--border-color)"
                }} onClick={() => document.getElementById("fileInput")?.click()}>
                  <input
                    type="file"
                    id="fileInput"
                    style={{ display: "none" }}
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={(e) => {
                      if (e.target.files && e.target.files.length > 0) {
                        setUploadFile(e.target.files[0]);
                      }
                    }}
                  />
                  <Upload size={40} color={uploadFile ? "var(--primary-light)" : "var(--text-muted)"} style={{ marginBottom: "12px" }} />
                  {uploadFile ? (
                    <div>
                      <p style={{ fontWeight: 600 }}>{uploadFile.name}</p>
                      <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{(uploadFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </div>
                  ) : (
                    <div>
                      <p style={{ fontWeight: 600 }}>Drag and drop your file here, or click to browse</p>
                      <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>Supports PDF, JPG, and PNG (Max 10MB)</p>
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={uploadProgress || !uploadFile}
                  className="premium-btn premium-btn-primary"
                  style={{ alignSelf: "flex-end" }}
                >
                  {uploadProgress ? "Uploading & Extracting..." : "Submit Application"}
                </button>
              </form>
            )}
          </div>
        )}

        {activeTab === "track" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <div className="glass-card">
              <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.4rem", marginBottom: "16px" }}>Track Permit Status</h3>
              <div style={{ display: "flex", gap: "12px" }}>
                <div style={{ flex: 1, position: "relative" }}>
                  <span style={{ position: "absolute", left: "14px", top: "12px", color: "var(--text-muted)" }}><Search size={16} /></span>
                  <input
                    type="text"
                    placeholder="Enter Application ID (e.g. PRM-2026-...)"
                    value={trackingId}
                    onChange={(e) => setTrackingId(e.target.value)}
                    className="premium-input"
                    style={{ paddingLeft: "42px" }}
                  />
                </div>
                <button 
                  onClick={() => handleTrackApplication(trackingId)}
                  disabled={trackingLoading}
                  className="premium-btn premium-btn-primary"
                >
                  {trackingLoading ? "Searching..." : "Track"}
                </button>
              </div>

              {trackingError && (
                <div style={{ background: "rgba(239, 68, 68, 0.15)", border: "1px solid var(--danger)", borderRadius: "8px", padding: "12px 16px", color: "#f87171", marginTop: "20px", fontSize: "0.85rem" }}>
                  {trackingError}
                </div>
              )}
            </div>

            {trackingResult && (
              <div className="glass-card animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                
                {/* Header Track Stats */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px", borderBottom: "1px solid var(--border-color)", paddingBottom: "20px" }}>
                  <div>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Permit Node Record</span>
                    <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.6rem" }}>{trackingResult.application_id}</h3>
                    <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", display: "flex", gap: "6px", marginTop: "4px" }}>
                      <Calendar size={14} /> Submitted {trackingResult.processing_days} days ago
                    </span>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "8px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Current Status:</span>
                      <span className={`status-badge status-${trackingResult.status}`}>{trackingResult.status}</span>
                    </div>
                    {trackingResult.quality_score !== null && (
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Form Completeness Score:</span>
                        <span style={{
                          fontWeight: 800,
                          color: trackingResult.quality_score >= 90 ? "var(--success)" : trackingResult.quality_score >= 70 ? "var(--accent)" : "var(--danger)"
                        }}>{trackingResult.quality_score}/100</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Timeline */}
                <div>
                  <h4 style={{ fontFamily: "var(--font-title)", fontSize: "1.1rem", marginBottom: "16px" }}>Process History Timeline</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "16px", position: "relative", paddingLeft: "24px" }}>
                    <div style={{ position: "absolute", left: "6px", top: "10px", bottom: "10px", width: "2px", background: "var(--border-color)" }}></div>
                    
                    {trackingResult.timeline.map((event: any, idx: number) => (
                      <div key={idx} style={{ position: "relative", display: "flex", gap: "16px" }}>
                        <div style={{
                          position: "absolute",
                          left: "-23px",
                          top: "4px",
                          width: "12px",
                          height: "12px",
                          borderRadius: "50%",
                          background: "var(--primary-light)",
                          boxShadow: "0 0 6px var(--primary-glow)"
                        }}></div>
                        <div>
                          <p style={{ fontWeight: 600, fontSize: "0.9rem" }}>{event.event}</p>
                          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                            {new Date(event.date).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions & Next Steps */}
                <div style={{ background: "rgba(255,255,255,0.02)", borderRadius: "12px", padding: "20px", border: "1px solid var(--border-color)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
                  <div style={{ maxWidth: "70%" }}>
                    <h5 style={{ fontWeight: 700, fontSize: "0.95rem", marginBottom: "4px" }}>Next Recommended Actions</h5>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{trackingResult.next_steps}</p>
                  </div>

                  {trackingResult.status === "approved" && (
                    <button 
                      onClick={() => handleDownloadCertificate(trackingResult.application_id)}
                      className="premium-btn premium-btn-success"
                      style={{ gap: "6px" }}
                    >
                      <Download size={16} />
                      <span>Download Permit PDF</span>
                    </button>
                  )}
                </div>

              </div>
            )}
          </div>
        )}

        {activeTab === "notifications" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Preferences */}
            <div className="glass-card">
              <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.4rem", marginBottom: "8px" }}>Notification Preferences</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "20px" }}>
                Select how you wish to receive updates regarding your applications.
              </p>
              
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "0.95rem" }}>
                  <input
                    type="checkbox"
                    checked={notifPreferences.email}
                    onChange={(e) => handleUpdatePreferences({ ...notifPreferences, email: e.target.checked })}
                    style={{ width: "16px", height: "16px", accentColor: "var(--primary)" }}
                  />
                  <span>Receive Email Updates via SendGrid</span>
                </label>

                <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "0.95rem" }}>
                  <input
                    type="checkbox"
                    checked={notifPreferences.sms}
                    onChange={(e) => handleUpdatePreferences({ ...notifPreferences, sms: e.target.checked })}
                    style={{ width: "16px", height: "16px", accentColor: "var(--primary)" }}
                  />
                  <span>Receive SMS Alerts (SMS Gateways)</span>
                </label>

                <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "0.95rem" }}>
                  <input
                    type="checkbox"
                    checked={notifPreferences.in_app}
                    onChange={(e) => handleUpdatePreferences({ ...notifPreferences, in_app: e.target.checked })}
                    style={{ width: "16px", height: "16px", accentColor: "var(--primary)" }}
                  />
                  <span>Enable In-App Logs & Popups</span>
                </label>
              </div>
            </div>

            {/* Notification logs list */}
            <div className="glass-card">
              <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.4rem", marginBottom: "16px" }}>In-App Logs History</h3>
              {notifications.length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>No notifications logged.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  {notifications.map((n) => (
                    <div key={n.id} style={{
                      padding: "16px",
                      background: n.is_read ? "rgba(255,255,255,0.01)" : "rgba(79, 70, 229, 0.05)",
                      border: "1px solid var(--border-color)",
                      borderRadius: "8px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}>
                      <div>
                        <p style={{ fontWeight: 600, fontSize: "0.9rem", color: n.is_read ? "#d1d5db" : "#fff" }}>{n.title}</p>
                        <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "2px" }}>{n.message}</p>
                        <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block", marginTop: "4px" }}>
                          {new Date(n.timestamp).toLocaleString()}
                        </span>
                      </div>
                      {!n.is_read && (
                        <button 
                          onClick={() => handleMarkNotifRead(n.id)}
                          className="premium-btn premium-btn-secondary"
                          style={{ padding: "6px 12px", fontSize: "0.75rem" }}
                        >
                          Mark Read
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        )}

      </div>

    </div>
  );
};
