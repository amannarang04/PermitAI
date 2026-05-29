import React, { useState } from "react";
import { Globe, Moon, Sun, Bell, LogOut, Shield, User } from "lucide-react";
import { STATES_CONFIG } from "../stateConfig";
import type { StateConfiguration } from "../stateConfig";


interface NavbarProps {
  selectedState: StateConfiguration;
  onStateChange: (state: StateConfiguration) => void;
  user: any;
  onLogout: () => void;
  lightMode: boolean;
  onToggleTheme: () => void;
  notificationCount: number;
  onOpenNotifications: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  selectedState,
  onStateChange,
  user,
  onLogout,
  lightMode,
  onToggleTheme,
  notificationCount,
  onOpenNotifications
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <nav style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "16px 32px",
      borderBottom: "1px solid var(--border-color)",
      background: "rgba(17, 24, 39, 0.6)",
      backdropFilter: "blur(12px)",
      position: "sticky",
      top: 0,
      zIndex: 100
    }}>
      {/* Brand Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", cursor: "pointer" }} onClick={() => window.location.hash = "#"}>
        <div style={{
          width: "40px",
          height: "40px",
          borderRadius: "8px",
          background: "linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 15px var(--primary-glow)",
          color: "#fff",
          fontWeight: "800",
          fontSize: "1.2rem"
        }}>
          P
        </div>
        <div>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 800, letterSpacing: "-0.03em", fontFamily: "var(--font-title)" }}>
            Permit<span style={{ color: "var(--primary-light)" }}>AI</span>
          </h2>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600 }}>
            {selectedState.authorityAbbr} Portal • {selectedState.name}
          </div>
        </div>
      </div>

      {/* Actions & Selector */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        
        {/* State Government Selector */}
        <div style={{ position: "relative" }}>
          <button 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="premium-btn premium-btn-secondary"
            style={{ padding: "8px 16px", fontSize: "0.85rem", gap: "6px" }}
          >
            <Globe size={16} color="var(--primary-light)" />
            <span>Govt. of {selectedState.name}</span>
          </button>
          
          {dropdownOpen && (
            <div style={{
              position: "absolute",
              top: "100%",
              right: 0,
              marginTop: "8px",
              background: "#1f2937",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
              width: "220px",
              overflow: "hidden",
              zIndex: 10
            }}>
              <div style={{ padding: "8px 12px", fontSize: "0.75rem", color: "var(--text-muted)", borderBottom: "1px solid var(--border-color)", fontWeight: 600 }}>
                SELECT STATE GOVERNMENT
              </div>
              {STATES_CONFIG.map(s => (
                <div 
                  key={s.id}
                  onClick={() => {
                    onStateChange(s);
                    setDropdownOpen(false);
                  }}
                  style={{
                    padding: "10px 16px",
                    cursor: "pointer",
                    fontSize: "0.85rem",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    background: selectedState.id === s.id ? "rgba(79, 70, 229, 0.1)" : "transparent",
                    color: selectedState.id === s.id ? "var(--primary-light)" : "#fff",
                    fontWeight: selectedState.id === s.id ? 600 : 400
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"}
                  onMouseLeave={(e) => e.currentTarget.style.background = selectedState.id === s.id ? "rgba(79, 70, 229, 0.1)" : "transparent"}
                >
                  <span>{s.name}</span>
                  <span style={{ fontSize: "0.75rem", opacity: 0.7 }}>{s.hindiName}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <button 
          onClick={onToggleTheme}
          style={{
            background: "none",
            border: "none",
            color: "var(--text-muted)",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            padding: "8px"
          }}
        >
          {lightMode ? <Moon size={20} /> : <Sun size={20} />}
        </button>

        {/* User Specific Buttons */}
        {user ? (
          <>
            {/* Notification Center Trigger */}
            <button 
              onClick={onOpenNotifications}
              style={{
                background: "none",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                position: "relative",
                display: "flex",
                alignItems: "center",
                padding: "8px"
              }}
            >
              <Bell size={20} />
              {notificationCount > 0 && (
                <span style={{
                  position: "absolute",
                  top: "2px",
                  right: "2px",
                  background: "var(--danger)",
                  color: "#fff",
                  fontSize: "0.65rem",
                  fontWeight: 800,
                  width: "16px",
                  height: "16px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 0 5px var(--danger-glow)"
                }}>
                  {notificationCount}
                </span>
              )}
            </button>

            {/* Profile Tag */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px", borderLeft: "1px solid var(--border-color)", paddingLeft: "16px" }}>
              <div style={{
                width: "32px",
                height: "32px",
                borderRadius: "50%",
                background: "rgba(255,255,255,0.05)",
                border: "1px solid var(--border-color)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--primary-light)"
              }}>
                {user.role === "admin" ? <Shield size={16} /> : <User size={16} />}
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>{user.username}</span>
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase" }}>{user.role}</span>
              </div>
            </div>

            {/* Logout */}
            <button 
              onClick={onLogout}
              className="premium-btn premium-btn-secondary"
              style={{ padding: "8px 12px", fontSize: "0.8rem", gap: "4px" }}
            >
              <LogOut size={14} />
              <span>Logout</span>
            </button>
          </>
        ) : (
          <button 
            onClick={() => window.location.hash = "#auth"}
            className="premium-btn premium-btn-primary"
            style={{ padding: "8px 16px", fontSize: "0.85rem" }}
          >
            Sign In
          </button>
        )}

      </div>
    </nav>
  );
};
