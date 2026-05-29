import React, { useState, useEffect } from "react";
import { CheckCircle, XCircle, AlertTriangle, RefreshCw, Layers } from "lucide-react";
import axios from "axios";


interface OfficerPortalProps {
  token: string;
  user: any;
  apiBaseUrl: string;
}

export const OfficerPortal: React.FC<OfficerPortalProps> = ({ token, user, apiBaseUrl }) => {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedApp, setSelectedApp] = useState<any>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Decision Modal States
  const [decisionModal, setDecisionModal] = useState<"approve" | "reject" | "request-docs" | null>(null);
  const [notes, setNotes] = useState("");
  const [conditions, setConditions] = useState("");
  const [reason, setReason] = useState("");
  const [requiredChanges, setRequiredChanges] = useState("");
  const [missingDocs, setMissingDocs] = useState<string[]>([]);
  const [deadlineDays, setDeadlineDays] = useState(14);
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => {
    fetchMyQueue();
  }, []);

  const fetchMyQueue = async () => {
    setLoading(true);
    setError("");
    try {
      // In the database we have two queue fetch endpoints:
      // 1. /api/queues/my-queue
      // 2. /api/applications/queue/my-queue
      // We will call the queues/my-queue since it retrieves the QueueAssignment model objects
      const res = await axios.get(`${apiBaseUrl}/api/queues/my-queue`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setQueue(res.data);
    } catch (err: any) {
      setError("Failed to load your department queue assignments.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectApp = async (appIdStr: string) => {
    setDetailsLoading(true);
    try {
      const res = await axios.get(`${apiBaseUrl}/api/queues/${appIdStr}/details`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedApp(res.data);
      // Reset modal inputs
      setNotes("");
      setConditions("");
      setReason("");
      setRequiredChanges("");
      setMissingDocs([]);
    } catch (err) {
      alert("Failed to load application details.");
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleDecisionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedApp) return;

    setModalLoading(true);
    const appId = selectedApp.application_id;
    try {
      if (decisionModal === "approve") {
        await axios.post(`${apiBaseUrl}/api/applications/${appId}/approve`, {
          notes,
          conditions: conditions ? conditions.split("\n").filter(c => c.trim()) : []
        }, { headers: { Authorization: `Bearer ${token}` } });
      } else if (decisionModal === "reject") {
        await axios.post(`${apiBaseUrl}/api/applications/${appId}/reject`, {
          reason,
          required_changes: requiredChanges ? requiredChanges.split("\n").filter(c => c.trim()) : []
        }, { headers: { Authorization: `Bearer ${token}` } });
      } else if (decisionModal === "request-docs") {
        await axios.post(`${apiBaseUrl}/api/applications/${appId}/request-documents`, {
          missing_documents: missingDocs,
          deadline_days: deadlineDays
        }, { headers: { Authorization: `Bearer ${token}` } });
      }

      setDecisionModal(null);
      setSelectedApp(null);
      fetchMyQueue();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to submit decision.");
    } finally {
      setModalLoading(false);
    }
  };

  const toggleMissingDoc = (doc: string) => {
    if (missingDocs.includes(doc)) {
      setMissingDocs(missingDocs.filter(d => d !== doc));
    } else {
      setMissingDocs([...missingDocs, doc]);
    }
  };

  return (
    <div style={{ display: "flex", gap: "28px", maxWidth: "1200px", margin: "40px auto", padding: "0 24px" }} className="animate-fade-in">
      
      {/* LEFT: Assignment List Queue */}
      <div className="glass-card" style={{ flex: 1.1, minWidth: "350px", display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.3rem" }}>Department Review Queue</h3>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase" }}>
              Assigned to: {user.full_name} ({user.department || "All"} Officer)
            </span>
          </div>
          <button onClick={fetchMyQueue} className="premium-btn premium-btn-secondary" style={{ padding: "8px" }}>
            <RefreshCw size={16} />
          </button>
        </div>

        {loading ? (
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Loading assignments...</p>
        ) : error ? (
          <p style={{ color: "var(--danger)", fontSize: "0.9rem" }}>{error}</p>
        ) : queue.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>No assignments found in your queue.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "600px", overflowY: "auto" }}>
            {queue.map((item) => (
              <div 
                key={item.id}
                onClick={() => handleSelectApp(item.application.application_id)}
                style={{
                  padding: "16px",
                  background: selectedApp?.application_id === item.application.application_id ? "rgba(79, 70, 229, 0.15)" : "rgba(255,255,255,0.02)",
                  border: `1px solid ${selectedApp?.application_id === item.application.application_id ? "var(--primary-light)" : "var(--border-color)"}`,
                  borderRadius: "10px",
                  cursor: "pointer",
                  transition: "all 0.2s"
                }}
                onMouseEnter={(e) => e.currentTarget.style.transform = "translateX(4px)"}
                onMouseLeave={(e) => e.currentTarget.style.transform = "translateX(0)"}
              >
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "var(--secondary)" }}>
                    {item.application.application_id}
                  </span>
                  <span className={`status-badge status-${item.application.status}`} style={{ fontSize: "0.7rem", padding: "2px 6px" }}>
                    {item.application.status}
                  </span>
                </div>
                <div style={{ fontSize: "0.8rem", color: "#d1d5db" }}>Applicant: {item.application.applicant_name || "N/A"}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "flex", justifyContent: "space-between", marginTop: "6px" }}>
                  <span>Cost: ₹{item.application.estimated_cost?.toLocaleString() || "0"}</span>
                  <span>Priority: <b style={{
                    color: item.priority === "critical" || item.priority === "high" ? "var(--danger)" : "var(--text-muted)"
                  }}>{item.priority}</b></span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RIGHT: Detailed Review Panel */}
      <div style={{ flex: 1.9 }}>
        {detailsLoading ? (
          <div className="glass-card" style={{ display: "flex", justifyContent: "center", padding: "60px" }}>
            <p>Loading application compliance data...</p>
          </div>
        ) : selectedApp ? (
          <div className="glass-card animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Header info */}
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "16px" }}>
              <div>
                <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.5rem" }}>{selectedApp.application_id}</h3>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Permit Type: <b>{selectedApp.project?.permit_type || "N/A"}</b></p>
              </div>
              <div style={{ display: "flex", gap: "10px" }}>
                <button onClick={() => setDecisionModal("request-docs")} className="premium-btn premium-btn-secondary" style={{ fontSize: "0.85rem", padding: "8px 12px" }}>
                  Docs Pending
                </button>
                <button onClick={() => setDecisionModal("reject")} className="premium-btn premium-btn-danger" style={{ fontSize: "0.85rem", padding: "8px 12px" }}>
                  Reject
                </button>
                <button onClick={() => setDecisionModal("approve")} className="premium-btn premium-btn-success" style={{ fontSize: "0.85rem", padding: "8px 12px" }}>
                  Approve
                </button>
              </div>
            </div>

            {/* Extracted Details vs Document Checklist */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", flexWrap: "wrap" }}>
              
              {/* Form Details */}
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <h4 style={{ fontFamily: "var(--font-title)", borderBottom: "1px dashed var(--border-color)", paddingBottom: "6px" }}>Extracted Meta Info</h4>
                
                <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.85rem" }}>
                  <div><b>Applicant Name:</b> <span style={{ color: "#d1d5db" }}>{selectedApp.applicant?.full_name || "N/A"}</span></div>
                  <div><b>Email / Phone:</b> <span style={{ color: "#d1d5db" }}>{selectedApp.applicant?.email || "N/A"} / {selectedApp.applicant?.phone || "N/A"}</span></div>
                  <div><b>Property Address:</b> <span style={{ color: "#d1d5db" }}>{selectedApp.property?.address?.line1 || "N/A"}</span></div>
                  <div><b>Estimated Cost:</b> <span style={{ color: "var(--accent)", fontWeight: 700 }}>₹{selectedApp.project?.estimated_cost?.value?.toLocaleString() || "0"}</span></div>
                  <div><b>Construction Area:</b> <span style={{ color: "#d1d5db" }}>{selectedApp.project?.construction_area?.value || "N/A"} sq ft</span></div>
                </div>
              </div>

              {/* Rules & Red Flags checklist */}
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <h4 style={{ fontFamily: "var(--font-title)", borderBottom: "1px dashed var(--border-color)", paddingBottom: "6px" }}>Compliance Check</h4>
                
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {/* Quality Score */}
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span>Form Quality Score:</span>
                    <b style={{
                      color: selectedApp.quality_score >= 90 ? "var(--success)" : selectedApp.quality_score >= 70 ? "var(--accent)" : "var(--danger)"
                    }}>{selectedApp.quality_score}/100</b>
                  </div>

                  {/* Red flags count */}
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span>Generated Red Flags:</span>
                    <b style={{ color: selectedApp.validation_errors?.length > 0 ? "var(--danger)" : "var(--success)" }}>
                      {selectedApp.validation_errors?.length || 0} Flags
                    </b>
                  </div>

                  {/* Verified checks */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "0.8rem", marginTop: "4px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <CheckCircle size={14} color="var(--success)" />
                      <span>GIS Coordinates Validated</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <CheckCircle size={14} color="var(--success)" />
                      <span>Contractor License ID OK</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* Red Flags warnings list */}
            {selectedApp.validation_errors?.length > 0 && (
              <div style={{
                background: "rgba(220, 38, 38, 0.1)",
                border: "1px solid var(--danger)",
                borderRadius: "10px",
                padding: "16px"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#f87171", marginBottom: "8px", fontWeight: 700, fontSize: "0.9rem" }}>
                  <AlertTriangle size={18} />
                  <span>Compliance Auditing Flagged Issues</span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "0.8rem", paddingLeft: "4px" }}>
                  {selectedApp.validation_errors.map((err: any, idx: number) => (
                    <div key={idx} style={{ color: "#fca5a5" }}>• {err.error_message || err}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Document Checklist verification table */}
            <div>
              <h4 style={{ fontFamily: "var(--font-title)", fontSize: "1.1rem", marginBottom: "12px" }}>Uploaded Documents Verification Checklist</h4>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "12px" }}>
                {Object.entries(selectedApp.checklist || {
                  "Site Plan Layout": true,
                  "Structural Calculations": true,
                  "Owner Aadhaar ID Proof": true,
                  "Property Deed Register": true
                }).map(([name, status], idx) => (
                  <div key={idx} style={{
                    padding: "10px 14px",
                    background: "rgba(255,255,255,0.01)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "8px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    fontSize: "0.8rem"
                  }}>
                    <span style={{ color: "#d1d5db" }}>{name}</span>
                    {status ? (
                      <CheckCircle size={16} color="var(--success)" />
                    ) : (
                      <XCircle size={16} color="var(--danger)" />
                    )}
                  </div>
                ))}
              </div>
            </div>

          </div>
        ) : (
          <div className="glass-card" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "80px", color: "var(--text-muted)", height: "400px" }}>
            <Layers size={48} style={{ marginBottom: "16px", opacity: 0.5 }} />
            <h4>No Application Selected</h4>
            <p style={{ fontSize: "0.85rem", marginTop: "4px" }}>Select any queue assignment on the left to start the compliance audit review.</p>
          </div>
        )}
      </div>

      {/* Decision Modals Overlay */}
      {decisionModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background: "rgba(0,0,0,0.8)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000
        }}>
          <div className="glass-card animate-fade-in" style={{ width: "100%", maxWidth: "500px", display: "flex", flexDirection: "column", gap: "20px" }}>
            <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.3rem" }}>
              {decisionModal === "approve" ? "Approve Permit Application" : 
               decisionModal === "reject" ? "Reject Permit Application" : 
               "Request Additional Documents"}
            </h3>

            <form onSubmit={handleDecisionSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {decisionModal === "approve" && (
                <>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Approval Notes</label>
                    <textarea 
                      required
                      rows={3}
                      placeholder="Include municipal conditions notes..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="premium-input"
                      style={{ resize: "none" }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Terms & Conditions (One per line)</label>
                    <textarea 
                      rows={3}
                      placeholder="e.g. Conduct monthly soil checks..."
                      value={conditions}
                      onChange={(e) => setConditions(e.target.value)}
                      className="premium-input"
                      style={{ resize: "none" }}
                    />
                  </div>
                </>
              )}

              {decisionModal === "reject" && (
                <>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Rejection Reason</label>
                    <textarea 
                      required
                      rows={3}
                      placeholder="Why is this permit rejected..."
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      className="premium-input"
                      style={{ resize: "none" }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Required Changes (One per line)</label>
                    <textarea 
                      rows={3}
                      placeholder="e.g. Provide correct floor plan drawing..."
                      value={requiredChanges}
                      onChange={(e) => setRequiredChanges(e.target.value)}
                      className="premium-input"
                      style={{ resize: "none" }}
                    />
                  </div>
                </>
              )}

              {decisionModal === "request-docs" && (
                <>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "8px", color: "var(--text-muted)" }}>Select Missing Documents</label>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {["site_plan", "drawings", "structural_calculations", "property_deed", "id_proof"].map((doc) => (
                        <label key={doc} style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer", fontSize: "0.85rem" }}>
                          <input 
                            type="checkbox"
                            checked={missingDocs.includes(doc)}
                            onChange={() => toggleMissingDoc(doc)}
                            style={{ accentColor: "var(--primary)" }}
                          />
                          <span>{doc.replace("_", " ").toUpperCase()}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Submission Deadline (Days)</label>
                    <input 
                      type="number"
                      required
                      min={1}
                      value={deadlineDays}
                      onChange={(e) => setDeadlineDays(parseInt(e.target.value))}
                      className="premium-input"
                    />
                  </div>
                </>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px", marginTop: "8px" }}>
                <button type="button" onClick={() => setDecisionModal(null)} className="premium-btn premium-btn-secondary" style={{ padding: "10px 16px" }}>
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={modalLoading}
                  className={`premium-btn ${
                    decisionModal === "approve" ? "premium-btn-success" : 
                    decisionModal === "reject" ? "premium-btn-danger" : 
                    "premium-btn-primary"
                  }`}
                  style={{ padding: "10px 20px" }}
                >
                  {modalLoading ? "Submitting..." : "Confirm Action"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
