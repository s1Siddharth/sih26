import React, { useState } from 'react';
import { Radar, Layers3, FileText, Menu, X } from 'lucide-react';

const NAV_ITEMS = [
  { id: 'demand', label: 'Market Demand', icon: Radar },
  { id: 'course-gap', label: 'Course Gap', icon: Layers3 },
  { id: 'resume', label: 'Resume Alignment', icon: FileText },
];

export default function Navbar({ activePage, onNavigate, user, onLoginClick, onLogout }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sb-header">
      {/* Gov topbar */}
      <div className="sb-topbar">
        <div className="sb-topbar-inner">
          <div className="sb-topbar-left">
            <span>🇮🇳</span>
            <span>Maharashtra · Skills, Employment &amp; Entrepreneurship</span>
          </div>
          <div className="sb-topbar-right">
            <span>SIH 2026 · PS #26134</span>
            <span className="sep">|</span>
            <span>Maharashtra focus</span>
          </div>
        </div>
      </div>

      {/* Brand + auth row */}
      <div className="sb-brandbar">
        <div className="sb-brandbar-inner">
          <div className="sb-brand">
            <div className="sb-logo"><Radar size={20} color="#D97706" /></div>
            <div>
              <div className="sb-brand-name">SkillBridge <span className="mh-pill">MH</span></div>
              <div className="sb-brand-sub">Labour-market intelligence · curriculum alignment</div>
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="sb-nav">
        <div className="sb-nav-inner">
          <div className={`sb-nav-links ${mobileOpen ? 'open' : ''}`}>
            {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
              <button key={id}
                className={`sb-nav-item ${activePage === id ? 'active' : ''}`}
                onClick={() => { onNavigate(id); setMobileOpen(false); }}
              >
                <Icon size={15} />
                <span>{label}</span>
              </button>
            ))}
          </div>
          <button className="sb-hamburger" onClick={() => setMobileOpen(o => !o)}>
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </nav>
    </header>
  );
}
