import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Globe, 
  Layers,
  Mail, 
  BarChart3, 
  History, 
  BookOpen, 
  Activity,
  Cpu
} from 'lucide-react';
import { HealthData } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: HealthData | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, health }) => {
  const navItems = [
    { id: 'overview', label: 'Dashboard', icon: Activity },
    { id: 'url', label: 'URL Scanner', icon: Globe },
    { id: 'bulk', label: 'Bulk Triage', icon: Layers },
    { id: 'email', label: 'Email Scanner', icon: Mail },
    { id: 'evaluation', label: 'Model Evaluation', icon: BarChart3 },
    { id: 'history', label: 'Scan History', icon: History },
    { id: 'about', label: 'Methodology', icon: BookOpen },
  ];

  const isHealthy = health?.status === 'healthy';
  const modelsReady = health?.models_ready ?? false;

  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800">
      <div className="w-full px-4 sm:px-6 lg:px-10">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => setActiveTab('overview')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-400 p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <ShieldAlert className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-cyan-400 via-teal-300 to-white bg-clip-text text-transparent">
                  PhishGuard
                </span>
                <span className="text-[10px] uppercase font-mono font-semibold tracking-wider px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-800 text-cyan-400">
                  XAI Defense
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono hidden sm:block">Explainable Phishing Intelligence</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-slate-900 border border-cyan-500/40 text-cyan-400 shadow-sm shadow-cyan-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* System Status Pill */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-400">Models:</span>
              <div className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${modelsReady ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
                <span className={modelsReady ? 'text-emerald-400 font-medium' : 'text-amber-400'}>
                  {modelsReady ? 'Active' : 'Missing'}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-cyan-400' : 'bg-rose-500'}`} />
              <span className={isHealthy ? 'text-slate-300' : 'text-rose-400'}>
                {isHealthy ? 'API Online' : 'Degraded'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Bar */}
        <div className="md:hidden flex items-center justify-between overflow-x-auto py-2 border-t border-slate-800/60 no-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center gap-1 px-3 py-1 rounded text-xs whitespace-nowrap ${
                  isActive ? 'text-cyan-400 font-semibold' : 'text-slate-400'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
