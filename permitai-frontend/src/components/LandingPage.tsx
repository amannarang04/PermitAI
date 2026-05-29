import React from "react";
import { ShieldCheck, Award, FileText, ChevronRight, BarChart2, ShieldAlert, Cpu } from "lucide-react";
import type { StateConfiguration } from "../stateConfig";

interface LandingPageProps {
  selectedState: StateConfiguration;
  onEnterPortal: (role: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ selectedState, onEnterPortal }) => {
  return (
    <div style={{ padding: "0 0 80px 0" }} className="animate-fade-in">
      
      {/* Hero Section */}
      <header style={{
        padding: "100px 32px 80px 32px",
        textAlign: "center",
        position: "relative",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        alignItems: "center"
      }}>
        
        {/* State Badge Banner */}
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "8px",
          padding: "6px 16px",
          background: "var(--primary-glow)",
          border: "1px solid var(--primary-light)",
          borderRadius: "9999px",
          fontSize: "0.85rem",
          fontWeight: 600,
          color: "#fff",
          marginBottom: "24px"
        }}>
          <span style={{
            width: "8px",
            height: "8px",
            background: "#10b981",
            borderRadius: "50%",
            boxShadow: "0 0 8px #10b981"
          }}></span>
          Active State Node: Govt. of {selectedState.name} ({selectedState.authorityAbbr})
        </div>

        <h1 style={{
          fontSize: "clamp(2.5rem, 5vw, 4rem)",
          fontWeight: 800,
          fontFamily: "var(--font-title)",
          maxWidth: "900px",
          lineHeight: 1.15,
          letterSpacing: "-0.04em",
          marginBottom: "24px"
        }}>
          Next-Generation AI <br/>
          <span style={{
            background: "linear-gradient(135deg, var(--primary-light) 0%, var(--secondary) 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}>
            Building Permit & Governance
          </span> Portal
        </h1>

        <p style={{
          color: "var(--text-muted)",
          fontSize: "1.15rem",
          maxWidth: "600px",
          marginBottom: "40px",
          lineHeight: 1.6
        }}>
          A unified, fully automated permit evaluation system powered by AI. Engineered for compliance review, fraud detection, and instant digital certificate delivery.
        </p>

        {/* Portal Entry Buttons */}
        <div style={{
          display: "flex",
          gap: "16px",
          flexWrap: "wrap",
          justifyContent: "center",
          marginBottom: "60px"
        }}>
          <button 
            onClick={() => onEnterPortal("citizen")}
            className="premium-btn premium-btn-primary"
            style={{ fontSize: "1.05rem", padding: "14px 28px" }}
          >
            <span>Citizen Portal</span>
            <ChevronRight size={18} />
          </button>
          
          <button 
            onClick={() => onEnterPortal("officer")}
            className="premium-btn premium-btn-secondary"
            style={{ fontSize: "1.05rem", padding: "14px 28px" }}
          >
            <span>Officer Console</span>
            <ShieldCheck size={18} />
          </button>

          <button 
            onClick={() => onEnterPortal("admin")}
            className="premium-btn premium-btn-secondary"
            style={{ fontSize: "1.05rem", padding: "14px 28px", border: "1px dashed var(--primary-light)" }}
          >
            <span>Supervisor Dashboard</span>
            <BarChart2 size={18} />
          </button>
        </div>

        {/* Mini Mockup Visual */}
        <div style={{
          width: "100%",
          maxWidth: "1000px",
          height: "450px",
          background: "rgba(10, 15, 30, 0.8)",
          borderRadius: "20px",
          border: "1px solid var(--border-color)",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.5), inset 0 0 40px rgba(79, 70, 229, 0.1)",
          overflow: "hidden",
          position: "relative",
          display: "flex",
          flexDirection: "column"
        }} className="neon-glow-primary">
          <div style={{
            height: "40px",
            background: "rgba(255,255,255,0.02)",
            borderBottom: "1px solid var(--border-color)",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            gap: "6px"
          }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#ef4444" }}></span>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#f59e0b" }}></span>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#10b981" }}></span>
            <span style={{ marginLeft: "12px", fontSize: "0.75rem", color: "var(--text-muted)" }}>
              https://permitai.{selectedState.id}.gov.in/portal
            </span>
          </div>
          
          <div style={{ flex: 1, display: "flex", padding: "24px", gap: "24px" }}>
            <div style={{ width: "30%", borderRight: "1px solid var(--border-color)", display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ height: "40px", background: "rgba(79, 70, 229, 0.15)", borderRadius: "8px", border: "1px solid var(--primary-glow)" }}></div>
              <div style={{ height: "30px", background: "rgba(255,255,255,0.02)", borderRadius: "8px" }}></div>
              <div style={{ height: "30px", background: "rgba(255,255,255,0.02)", borderRadius: "8px" }}></div>
              <div style={{ height: "30px", background: "rgba(255,255,255,0.02)", borderRadius: "8px" }}></div>
            </div>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 style={{ fontFamily: "var(--font-title)", fontSize: "1.1rem" }}>Compliance Evaluator</h3>
                <span className="status-badge status-processing">Analyzing Form...</span>
              </div>
              <div style={{ flex: 1, background: "rgba(0,0,0,0.2)", borderRadius: "12px", border: "1px solid var(--border-color)", padding: "16px", display: "flex", flexDirection: "column", gap: "10px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  <span>Extraction Confidence:</span>
                  <span style={{ color: "var(--success)", fontWeight: 800 }}>98.6%</span>
                </div>
                <div style={{ height: "8px", background: "rgba(255,255,255,0.05)", borderRadius: "4px", overflow: "hidden" }}>
                  <div style={{ width: "98.6%", height: "100%", background: "var(--success)" }}></div>
                </div>
                <div style={{ borderTop: "1px dashed var(--border-color)", paddingTop: "12px", marginTop: "8px", display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div style={{ display: "flex", gap: "8px", alignItems: "center", fontSize: "0.8rem" }}>
                    <ShieldAlert size={14} color="var(--accent)" />
                    <span>Cost Deviation Check: <b>Normal</b> (+2.4% vs state market avg)</span>
                  </div>
                  <div style={{ display: "flex", gap: "8px", alignItems: "center", fontSize: "0.8rem" }}>
                    <Award size={14} color="var(--success)" />
                    <span>Contractor License ID: <b>Verified</b> (LIC-CON-2022-9981)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </header>

      {/* Metrics Banner Section */}
      <section style={{
        background: "rgba(10, 15, 30, 0.4)",
        borderTop: "1px solid var(--border-color)",
        borderBottom: "1px solid var(--border-color)",
        padding: "40px 32px",
        marginBottom: "80px"
      }}>
        <div style={{
          maxWidth: "1100px",
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "32px",
          textAlign: "center"
        }}>
          <div>
            <h2 style={{ fontSize: "2.5rem", color: "var(--primary-light)" }}>&lt; 2.4 Hrs</h2>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Average Processing Speed</p>
          </div>
          <div>
            <h2 style={{ fontSize: "2.5rem", color: "var(--secondary)" }}>98.6%</h2>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>AI Extraction Accuracy</p>
          </div>
          <div>
            <h2 style={{ fontSize: "2.5rem", color: "var(--accent)" }}>0%</h2>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Manual Processing Bottlenecks</p>
          </div>
          <div>
            <h2 style={{ fontSize: "2.5rem", color: "var(--success)" }}>Verified</h2>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Pan-India Regulation Check</p>
          </div>
        </div>
      </section>

      {/* Core SaaS Features Grid */}
      <section style={{ maxWidth: "1100px", margin: "0 auto", padding: "0 32px" }}>
        
        <h2 style={{
          textAlign: "center",
          fontFamily: "var(--font-title)",
          fontSize: "2.2rem",
          marginBottom: "12px"
        }}>
          Autonomous Compliance Platform
        </h2>
        
        <p style={{
          textAlign: "center",
          color: "var(--text-muted)",
          maxWidth: "600px",
          margin: "0 auto 48px auto",
          fontSize: "1rem"
        }}>
          Every building application undergoes direct AI-based extraction, rule engine checks, and fraud heuristics in minutes.
        </p>

        <div className="premium-grid">
          
          <div className="glass-card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{
              width: "48px",
              height: "48px",
              borderRadius: "10px",
              background: "rgba(6, 182, 212, 0.1)",
              border: "1px solid rgba(6, 182, 212, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--secondary)"
            }}>
              <Cpu size={24} />
            </div>
            <h3 style={{ fontFamily: "var(--font-title)" }}>AI Document OCR & Extraction</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
              Automatic extraction of citizen details, property sizes, coordinates, estimated costs, and contractors utilizing advanced multi-modal models.
            </p>
          </div>

          <div className="glass-card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{
              width: "48px",
              height: "48px",
              borderRadius: "10px",
              background: "rgba(245, 158, 11, 0.1)",
              border: "1px solid rgba(245, 158, 11, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--accent)"
            }}>
              <ShieldAlert size={24} />
            </div>
            <h3 style={{ fontFamily: "var(--font-title)" }}>Cost Variance & Fraud Guard</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
              Compares construction estimates with state property values. Flags contractor permit velocity and alerts municipal teams to suspicious under-evaluations.
            </p>
          </div>

          <div className="glass-card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{
              width: "48px",
              height: "48px",
              borderRadius: "10px",
              background: "rgba(16, 185, 129, 0.1)",
              border: "1px solid rgba(16, 185, 129, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--success)"
            }}>
              <FileText size={24} />
            </div>
            <h3 style={{ fontFamily: "var(--font-title)" }}>Dynamic Digital Certificates</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
              Generates official, print-ready building permit certificate PDFs formatted dynamically based on the active state authority and municipal laws.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
};
