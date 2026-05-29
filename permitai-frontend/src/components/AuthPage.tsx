import React, { useState } from "react";
import { User, Lock, Mail, ShieldAlert, Key } from "lucide-react";
import axios from "axios";

interface AuthPageProps {
  onLoginSuccess: (token: string, user: any) => void;
  apiBaseUrl: string;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onLoginSuccess, apiBaseUrl }) => {
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");

  // Login fields
  const [loginUser, setLoginUser] = useState("");
  const [loginPass, setLoginPass] = useState("");

  // Register fields
  const [regUser, setRegUser] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPass, setRegPass] = useState("");
  const [regName, setRegName] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      // API expects form-data for OAuth2 Password Flow
      const params = new URLSearchParams();
      params.append("username", loginUser);
      params.append("password", loginPass);

      const response = await axios.post(`${apiBaseUrl}/api/auth/login`, params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });

      const { access_token } = response.data;

      // Get current user details using token
      const userRes = await axios.get(`${apiBaseUrl}/api/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });

      onLoginSuccess(access_token, userRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccessMsg("");
    try {
      await axios.post(`${apiBaseUrl}/api/auth/register`, {
        username: regUser,
        email: regEmail,
        password: regPass,
        full_name: regName
      });
      setSuccessMsg("Registration successful! Please login.");
      setActiveTab("login");
      setLoginUser(regUser);
      setLoginPass(regPass);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to register. Username or email may be taken.");
    } finally {
      setLoading(false);
    }
  };

  // Helper function for sandbox quick-login
  const handleQuickLogin = async (username: string) => {
    setLoading(true);
    setError("");
    const password = username.includes("officer") ? "officerpassword" : `${username}password`;
    try {
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);

      const response = await axios.post(`${apiBaseUrl}/api/auth/login`, params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });

      const { access_token } = response.data;
      const userRes = await axios.get(`${apiBaseUrl}/api/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      onLoginSuccess(access_token, userRes.data);
    } catch (err: any) {
      setError(`Quick Login failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: "flex",
      gap: "40px",
      maxWidth: "1000px",
      margin: "60px auto",
      padding: "0 24px",
      flexWrap: "wrap",
      alignItems: "stretch"
    }} className="animate-fade-in">

      {/* Form Card */}
      <div className="glass-card" style={{ flex: 1.2, minWidth: "320px", display: "flex", flexDirection: "column" }}>

        {/* Tabs switcher */}
        <div style={{
          display: "flex",
          background: "rgba(255, 255, 255, 0.03)",
          borderRadius: "8px",
          padding: "4px",
          marginBottom: "24px",
          border: "1px solid var(--border-color)"
        }}>
          <button
            onClick={() => { setActiveTab("login"); setError(""); }}
            style={{
              flex: 1,
              padding: "10px",
              background: activeTab === "login" ? "var(--primary)" : "none",
              border: "none",
              color: activeTab === "login" ? "#fff" : "var(--text-muted)",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.9rem",
              transition: "all 0.2s"
            }}
          >
            Sign In
          </button>
          <button
            onClick={() => { setActiveTab("register"); setError(""); }}
            style={{
              flex: 1,
              padding: "10px",
              background: activeTab === "register" ? "var(--primary)" : "none",
              border: "none",
              color: activeTab === "register" ? "#fff" : "var(--text-muted)",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.9rem",
              transition: "all 0.2s"
            }}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div style={{
            background: "rgba(239, 68, 68, 0.15)",
            border: "1px solid var(--danger)",
            borderRadius: "8px",
            padding: "12px 16px",
            color: "#f87171",
            fontSize: "0.85rem",
            marginBottom: "20px",
            display: "flex",
            gap: "8px",
            alignItems: "center"
          }}>
            <ShieldAlert size={16} />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div style={{
            background: "rgba(16, 185, 129, 0.15)",
            border: "1px solid var(--success)",
            borderRadius: "8px",
            padding: "12px 16px",
            color: "#34d399",
            fontSize: "0.85rem",
            marginBottom: "20px"
          }}>
            {successMsg}
          </div>
        )}

        {activeTab === "login" ? (
          <form onSubmit={handleLoginSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Username</label>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: "14px", top: "12px", color: "var(--text-muted)" }}><User size={16} /></span>
                <input
                  type="text"
                  required
                  placeholder="Enter username"
                  value={loginUser}
                  onChange={(e) => setLoginUser(e.target.value)}
                  className="premium-input"
                  style={{ paddingLeft: "42px" }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Password</label>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: "14px", top: "12px", color: "var(--text-muted)" }}><Lock size={16} /></span>
                <input
                  type="password"
                  required
                  placeholder="Enter password"
                  value={loginPass}
                  onChange={(e) => setLoginPass(e.target.value)}
                  className="premium-input"
                  style={{ paddingLeft: "42px" }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="premium-btn premium-btn-primary"
              style={{ width: "100%", marginTop: "8px" }}
            >
              {loading ? "Authenticating..." : "Sign In to Portal"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegisterSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Full Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Rajesh Kumar"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                className="premium-input"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Username</label>
              <input
                type="text"
                required
                placeholder="Pick a username"
                value={regUser}
                onChange={(e) => setRegUser(e.target.value)}
                className="premium-input"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Email Address</label>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: "14px", top: "12px", color: "var(--text-muted)" }}><Mail size={16} /></span>
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="premium-input"
                  style={{ paddingLeft: "42px" }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "6px", color: "var(--text-muted)" }}>Password</label>
              <input
                type="password"
                required
                placeholder="Min 6 characters"
                value={regPass}
                onChange={(e) => setRegPass(e.target.value)}
                className="premium-input"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="premium-btn premium-btn-primary"
              style={{ width: "100%", marginTop: "8px" }}
            >
              {loading ? "Registering..." : "Create Account"}
            </button>
          </form>
        )}

      </div>

      {/* Sandbox Quick Access Guide */}
      <div className="glass-card" style={{
        flex: 0.8,
        minWidth: "280px",
        background: "rgba(30, 41, 59, 0.4)",
        border: "1px dashed var(--primary-glow)",
        display: "flex",
        flexDirection: "column",
        gap: "16px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Key size={20} color="var(--primary-light)" />
          <h3 style={{ fontFamily: "var(--font-title)" }}>Sandbox Helper</h3>
        </div>
        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
          Use the quick-login buttons below to instantly bypass input forms and test predefined authority profiles.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "12px" }}>
          <div>
            <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "4px" }}>CITIZEN PROFILE</div>
            <button
              onClick={() => handleQuickLogin("citizen")}
              className="premium-btn premium-btn-secondary"
              style={{ width: "100%", justifyContent: "flex-start", padding: "8px 12px", fontSize: "0.8rem" }}
            >
              👤 Rajesh Kumar (Citizen)
            </button>
          </div>

          <div>
            <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "4px" }}>OFFICER PROFILES</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <button
                onClick={() => handleQuickLogin("officer")}
                className="premium-btn premium-btn-secondary"
                style={{ width: "100%", justifyContent: "flex-start", padding: "8px 12px", fontSize: "0.8rem" }}
              >
                👮 Building Review Officer
              </button>
              <button
                onClick={() => handleQuickLogin("electrical_officer")}
                className="premium-btn premium-btn-secondary"
                style={{ width: "100%", justifyContent: "flex-start", padding: "8px 12px", fontSize: "0.8rem" }}
              >
                ⚡ Electrical Review Officer
              </button>
              <button
                onClick={() => handleQuickLogin("plumbing_officer")}
                className="premium-btn premium-btn-secondary"
                style={{ width: "100%", justifyContent: "flex-start", padding: "8px 12px", fontSize: "0.8rem" }}
              >
                💧 Plumbing Review Officer
              </button>
            </div>
          </div>

          <div>
            <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "4px" }}>MANAGEMENT PROFILES</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <button
                onClick={() => handleQuickLogin("supervisor")}
                className="premium-btn premium-btn-secondary"
                style={{ width: "100%", justifyContent: "flex-start", padding: "8px 12px", fontSize: "0.8rem" }}
              >
                📊 Department Supervisor
              </button>
              <button
                onClick={() => handleQuickLogin("admin")}
                className="premium-btn premium-btn-secondary"
                style={{ width: "100%", justifyContent: "flex-start", padding: "8px 12px", fontSize: "0.8rem" }}
              >
                ⚙️ System Administrator
              </button>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
