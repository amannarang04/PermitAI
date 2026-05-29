import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { LandingPage } from "./components/LandingPage";
import { AuthPage } from "./components/AuthPage";
import { CitizenPortal } from "./components/CitizenPortal";
import { OfficerPortal } from "./components/OfficerPortal";
import { AdminPortal } from "./components/AdminPortal";
import { getSelectedState, saveSelectedState } from "./stateConfig";
import type { StateConfiguration } from "./stateConfig";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const App: React.FC = () => {
  const [selectedState, setSelectedState] = useState<StateConfiguration>(getSelectedState());
  const [lightMode, setLightMode] = useState<boolean>(
    localStorage.getItem("theme_mode") === "light"
  );
  
  const [token, setToken] = useState<string | null>(localStorage.getItem("auth_token"));
  const [user, setUser] = useState<any>(null);
  const [hash, setHash] = useState<string>(window.location.hash || "#");
  const [notificationCount, setNotificationCount] = useState(0);

  // Sync hash routing
  useEffect(() => {
    const handleHashChange = () => setHash(window.location.hash || "#");
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  // Fetch current user details if token is stored
  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      setUser(null);
    }
  }, [token]);

  // Sync state configuration theme class and light/dark mode class on body element
  useEffect(() => {
    // Remove all state theme classes
    document.body.className = "";
    
    // Add current theme and state classes
    document.body.classList.add(selectedState.themeClass);
    if (lightMode) {
      document.body.classList.add("light-mode");
    }
  }, [selectedState, lightMode]);

  const fetchCurrentUser = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(res.data);
      
      // Fetch notification count if citizen/admin
      fetchNotificationsCount();
    } catch (err) {
      // Token expired or invalid
      handleLogout();
    }
  };

  const fetchNotificationsCount = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/notifications`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const unread = res.data.filter((n: any) => !n.is_read).length;
      setNotificationCount(unread);
    } catch (err) {}
  };

  const handleStateChange = (state: StateConfiguration) => {
    setSelectedState(state);
    saveSelectedState(state.id);
  };

  const handleToggleTheme = () => {
    const newVal = !lightMode;
    setLightMode(newVal);
    localStorage.setItem("theme_mode", newVal ? "light" : "dark");
  };

  const handleLoginSuccess = (newToken: string, loggedUser: any) => {
    setToken(newToken);
    setUser(loggedUser);
    localStorage.setItem("auth_token", newToken);
    
    // Redirect based on role
    if (loggedUser.role === "citizen") {
      window.location.hash = "#citizen";
    } else if (loggedUser.role === "officer" || loggedUser.role === "supervisor" || loggedUser.role === "director") {
      window.location.hash = "#officer";
    } else if (loggedUser.role === "admin") {
      window.location.hash = "#admin";
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("auth_token");
    window.location.hash = "#";
  };

  const handleEnterPortal = (role: string) => {
    if (!token) {
      window.location.hash = "#auth";
    } else {
      if (role === "citizen") window.location.hash = "#citizen";
      else if (role === "officer") window.location.hash = "#officer";
      else if (role === "admin") window.location.hash = "#admin";
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      
      {/* Background Blobs for Visual Sparkle */}
      <div className="blob-2"></div>

      <Navbar 
        selectedState={selectedState}
        onStateChange={handleStateChange}
        user={user}
        onLogout={handleLogout}
        lightMode={lightMode}
        onToggleTheme={handleToggleTheme}
        notificationCount={notificationCount}
        onOpenNotifications={() => {
          if (user && user.role === "citizen") {
            window.location.hash = "#citizen";
          }
        }}
      />

      {/* Main Body Routing Container */}
      <main style={{ flex: 1, position: "relative" }}>
        
        {hash === "#" && (
          <LandingPage 
            selectedState={selectedState}
            onEnterPortal={handleEnterPortal}
          />
        )}

        {hash === "#auth" && (
          <AuthPage 
            apiBaseUrl={API_BASE_URL}
            onLoginSuccess={handleLoginSuccess}
          />
        )}

        {hash === "#citizen" && (
          token && user ? (
            user.role === "citizen" || user.role === "admin" ? (
              <CitizenPortal 
                token={token}
                user={user}
                apiBaseUrl={API_BASE_URL}
              />
            ) : (
              <div className="glass-card animate-fade-in" style={{ maxWidth: "500px", margin: "80px auto", textAlign: "center" }}>
                <h3 style={{ fontFamily: "var(--font-title)", marginBottom: "8px" }}>Access Restrained</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>This dashboard portal is configured for Citizens only.</p>
                <button onClick={() => window.location.hash = "#"} className="premium-btn premium-btn-primary" style={{ marginTop: "20px" }}>
                  Go to Homepage
                </button>
              </div>
            )
          ) : (
            <AuthPage 
              apiBaseUrl={API_BASE_URL}
              onLoginSuccess={handleLoginSuccess}
            />
          )
        )}

        {hash === "#officer" && (
          token && user ? (
            user.role === "officer" || user.role === "supervisor" || user.role === "director" || user.role === "admin" ? (
              <OfficerPortal 
                token={token}
                user={user}
                apiBaseUrl={API_BASE_URL}
              />
            ) : (
              <div className="glass-card animate-fade-in" style={{ maxWidth: "500px", margin: "80px auto", textAlign: "center" }}>
                <h3 style={{ fontFamily: "var(--font-title)", marginBottom: "8px" }}>Access Restrained</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>This console workspace is restricted to Review Officers and Supervisors.</p>
                <button onClick={() => window.location.hash = "#"} className="premium-btn premium-btn-primary" style={{ marginTop: "20px" }}>
                  Go to Homepage
                </button>
              </div>
            )
          ) : (
            <AuthPage 
              apiBaseUrl={API_BASE_URL}
              onLoginSuccess={handleLoginSuccess}
            />
          )
        )}

        {hash === "#admin" && (
          token && user ? (
            user.role === "admin" || user.role === "supervisor" || user.role === "director" ? (
              <AdminPortal 
                token={token}
                apiBaseUrl={API_BASE_URL}
              />
            ) : (
              <div className="glass-card animate-fade-in" style={{ maxWidth: "500px", margin: "80px auto", textAlign: "center" }}>
                <h3 style={{ fontFamily: "var(--font-title)", marginBottom: "8px" }}>Access Restrained</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>This management console is restricted to System Administrators and Supervisors.</p>
                <button onClick={() => window.location.hash = "#"} className="premium-btn premium-btn-primary" style={{ marginTop: "20px" }}>
                  Go to Homepage
                </button>
              </div>
            )
          ) : (
            <AuthPage 
              apiBaseUrl={API_BASE_URL}
              onLoginSuccess={handleLoginSuccess}
            />
          )
        )}


      </main>

      {/* Footer */}
      <footer style={{
        textAlign: "center",
        padding: "32px",
        borderTop: "1px solid var(--border-color)",
        color: "var(--text-muted)",
        fontSize: "0.85rem",
        background: "rgba(10, 15, 30, 0.4)",
        marginTop: "auto"
      }}>
        <p>© 2026 PermitAI Inc. Unified National Portal for Building Compliance & Governance.</p>
        <p style={{ marginTop: "4px", fontSize: "0.75rem", opacity: 0.8 }}>
          Developed for BBMP Karnataka, BMC Maharashtra, MCD Delhi, GCC Tamil Nadu, and Municipalities across India.
        </p>
      </footer>

    </div>
  );
};

export default App;
