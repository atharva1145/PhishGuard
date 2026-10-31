import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewPage } from './pages/OverviewPage';
import { UrlScannerPage } from './pages/UrlScannerPage';
import { BulkScannerPage } from './pages/BulkScannerPage';
import { EmailScannerPage } from './pages/EmailScannerPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { HistoryPage } from './pages/HistoryPage';
import { AboutPage } from './pages/AboutPage';
import { HealthData } from './types';
import { checkHealth } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [health, setHealth] = useState<HealthData | null>(null);

  const fetchHealthStatus = async () => {
    try {
      const data = await checkHealth();
      setHealth(data);
    } catch (err) {
      setHealth({
        status: 'degraded',
        timestamp: new Date().toISOString(),
        database_status: 'unknown',
        models_ready: false,
        models: {
          url_classifier: { ready: false, size_bytes: 0 },
          email_classifier: { ready: false, size_bytes: 0 },
          all_ready: false
        }
      });
    }
  };

  useEffect(() => {
    fetchHealthStatus();
    const interval = setInterval(fetchHealthStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />

      <main className="flex-1 w-full px-4 sm:px-6 lg:px-10 py-8">
        {activeTab === 'overview' && <OverviewPage setActiveTab={setActiveTab} />}
        {activeTab === 'url' && <UrlScannerPage />}
        {activeTab === 'bulk' && <BulkScannerPage />}
        {activeTab === 'email' && <EmailScannerPage />}
        {activeTab === 'evaluation' && <EvaluationPage />}
        {activeTab === 'history' && <HistoryPage />}
        {activeTab === 'about' && <AboutPage />}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 mt-12 text-xs font-mono text-slate-400">
        <div className="w-full px-4 sm:px-6 lg:px-10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300">PhishGuard v1.0.0</span>
            <span>•</span>
            <span>Explainable AI Phishing Detection Platform</span>
          </div>
          <div className="text-center sm:text-right text-slate-400 text-[11px]">
            Trained on benchmark telemetry • Engineered with Scikit-learn, FastAPI, and React
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
