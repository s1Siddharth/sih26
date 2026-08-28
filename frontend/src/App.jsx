import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MarketDemandRadar from './components/MarketDemandRadar';
import CourseGapAnalyzer from './components/CourseGapAnalyzer';
import ResumeAlignment from './components/ResumeAlignment';
import './index.css';

export default function App() {
  const [activePage, setActivePage] = useState('demand');

  const renderPage = () => {
    switch (activePage) {
      case 'demand': return <MarketDemandRadar />;
      case 'course-gap': return <CourseGapAnalyzer />;
      case 'resume': return <ResumeAlignment />;
      default: return <MarketDemandRadar />;
    }
  };

  return (
    <div className="app">
      <Navbar
        activePage={activePage}
        onNavigate={setActivePage}
      />
      <main className="main-content">
        <div className="page-transition" key={activePage}>
          {renderPage()}
        </div>
      </main>
      <footer className="app-footer">
        <p>SkillBridge · SIH 2026 · PS #26134 · Maharashtra-focused prototype · Market evidence is demo data</p>
      </footer>
    </div>
  );
}
