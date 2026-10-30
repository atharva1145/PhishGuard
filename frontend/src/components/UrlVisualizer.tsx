import React, { useState } from 'react';
import { SyntaxToken } from '../types';
import { Eye, ShieldAlert, ShieldCheck, AlertTriangle, Info, Terminal } from 'lucide-react';

interface UrlVisualizerProps {
  tokens?: SyntaxToken[];
  rawUrl: string;
}

export const UrlVisualizer: React.FC<UrlVisualizerProps> = ({ tokens, rawUrl }) => {
  const [selectedToken, setSelectedToken] = useState<SyntaxToken | null>(
    tokens && tokens.length > 0 ? (tokens.find(t => t.is_suspicious) || tokens[0]) : null
  );

  if (!tokens || tokens.length === 0) {
    return null;
  }

  const getBadgeStyle = (token: SyntaxToken) => {
    switch (token.severity) {
      case 'HIGH':
        return 'bg-rose-950/70 border-rose-600 text-rose-300 hover:bg-rose-900/60 shadow-sm shadow-rose-950';
      case 'MEDIUM':
        return 'bg-amber-950/70 border-amber-600 text-amber-300 hover:bg-amber-900/60';
      case 'LOW':
        return 'bg-cyan-950/50 border-cyan-700 text-cyan-300 hover:bg-cyan-900/50';
      case 'SAFE':
        return 'bg-emerald-950/40 border-emerald-800 text-emerald-300 hover:bg-emerald-900/40';
      default:
        return 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800';
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-rose-950 border border-rose-800 text-rose-400">
            <ShieldAlert className="w-3 h-3" /> High Risk Token
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-amber-950 border border-amber-800 text-amber-400">
            <AlertTriangle className="w-3 h-3" /> Suspicious Structure
          </span>
        );
      case 'LOW':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-400">
            <Info className="w-3 h-3" /> Cautionary
          </span>
        );
      case 'SAFE':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400">
            <ShieldCheck className="w-3 h-3" /> Standard
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400">
            {severity}
          </span>
        );
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200 flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          Interactive URL Syntax Visualizer
        </h4>
        <span className="text-xs text-slate-400 font-mono hidden sm:inline">
          Click any segment to inspect threat rationale
        </span>
      </div>

      {/* Segmented Token Ribbon */}
      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/90 flex flex-wrap items-center gap-1.5 font-mono text-sm leading-relaxed overflow-x-auto">
        {tokens.map((token, idx) => {
          const isSelected = selectedToken === token;
          return (
            <button
              key={idx}
              onClick={() => setSelectedToken(token)}
              onMouseEnter={() => setSelectedToken(token)}
              className={`px-2.5 py-1 rounded-lg border text-xs sm:text-sm font-mono transition-all transform cursor-pointer ${getBadgeStyle(
                token
              )} ${isSelected ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-950 scale-105' : 'opacity-90 hover:opacity-100'}`}
              title={token.tooltip}
            >
              {token.text}
            </button>
          );
        })}
      </div>

      {/* Active Token Inspector Card */}
      {selectedToken && (
        <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2 animate-in fade-in duration-150">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/70 pb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-slate-400 uppercase">Segment:</span>
              <code className="text-sm font-mono font-bold text-white bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                {selectedToken.text}
              </code>
              <span className="text-xs font-mono text-cyan-400 capitalize">
                ({selectedToken.type.replace('_', ' ')})
              </span>
            </div>
            {getSeverityBadge(selectedToken.severity)}
          </div>

          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            <strong className="text-cyan-400 font-mono font-medium mr-1.5">Security Rationale:</strong>
            {selectedToken.tooltip}
          </p>
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800/60">
        <span className="text-slate-400">Legend:</span>
        <span className="flex items-center gap-1.5 text-rose-400">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> High-Risk Anomaly
        </span>
        <span className="flex items-center gap-1.5 text-amber-400">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Suspicious Token
        </span>
        <span className="flex items-center gap-1.5 text-cyan-400">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" /> Cautionary
        </span>
        <span className="flex items-center gap-1.5 text-emerald-400">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Legitimate / Standard
        </span>
      </div>
    </div>
  );
};
