import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Info, 
  Clock, 
  Cpu, 
  CheckCircle2, 
  FileText 
} from 'lucide-react';
import { RiskIndicator } from '../types';
import { RiskBadge } from './RiskBadge';

interface ExplanationCardProps {
  prediction: string;
  isPhishing: boolean;
  confidenceScore: number;
  phishingProbability: number;
  riskLevel: 'High' | 'Medium' | 'Low';
  explanation: string;
  riskIndicators: RiskIndicator[];
  modelVersion: string;
  timestamp: string;
  disclaimerOrWarning?: string;
  onExportReport?: () => void;
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({
  prediction,
  isPhishing,
  confidenceScore,
  phishingProbability,
  riskLevel,
  explanation,
  riskIndicators,
  modelVersion,
  timestamp,
  disclaimerOrWarning,
  onExportReport,
}) => {
  const probPercent = Math.round(phishingProbability * 100);
  const confPercent = Math.round(confidenceScore * 100);

  return (
    <div className="space-y-6">
      {/* Primary Result Banner */}
      <div 
        className={`p-6 rounded-2xl border backdrop-blur-md transition-all ${
          isPhishing 
            ? 'bg-rose-950/30 border-rose-900/60 shadow-lg shadow-rose-950/20' 
            : 'bg-emerald-950/30 border-emerald-900/60 shadow-lg shadow-emerald-950/20'
        }`}
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div className="flex items-center gap-3">
            <div 
              className={`w-12 h-12 rounded-xl flex items-center justify-center border ${
                isPhishing 
                  ? 'bg-rose-950 border-rose-800 text-rose-400' 
                  : 'bg-emerald-950 border-emerald-800 text-emerald-400'
              }`}
            >
              {isPhishing ? <ShieldAlert className="w-7 h-7" /> : <ShieldCheck className="w-7 h-7" />}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h3 className="text-xl font-bold tracking-tight text-white font-mono">
                  {prediction}
                </h3>
                <RiskBadge severity={riskLevel.toUpperCase() as any} size="sm" />
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Model Confidence: {confPercent}% ({probPercent}% Phishing Probability)
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {onExportReport && (
              <button
                onClick={onExportReport}
                className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-cyan-600 text-xs font-mono font-medium text-cyan-300 flex items-center gap-1.5 transition-all shadow-sm"
                title="Download complete incident investigation report (.txt)"
              >
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                Export Forensic Report
              </button>
            )}
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-950/60 px-2.5 py-1.5 rounded-lg border border-slate-800">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>{modelVersion}</span>
            </div>
          </div>
        </div>

        {/* Probability Meter Bar */}
        <div className="space-y-1.5 mt-2">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">Legitimate (0%)</span>
            <span className={`font-semibold ${isPhishing ? 'text-rose-400' : 'text-emerald-400'}`}>
              Phishing Probability: {probPercent}%
            </span>
            <span className="text-slate-400">Phishing (100%)</span>
          </div>
          <div className="h-2.5 w-full bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div 
              className={`h-full rounded-full transition-all duration-700 ease-out ${
                isPhishing 
                  ? 'bg-gradient-to-r from-amber-500 via-rose-500 to-rose-600' 
                  : 'bg-gradient-to-r from-emerald-600 to-teal-400'
              }`}
              style={{ width: `${Math.max(4, Math.min(100, probPercent))}%` }}
            />
          </div>
        </div>

        {/* Narrative Summary */}
        <div className="mt-4 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-sm leading-relaxed text-slate-200">
          <span className="font-semibold text-cyan-400 mr-1.5 font-mono">Analysis:</span>
          {explanation}
        </div>
      </div>

      {/* Detected Risk Indicators */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-cyan-400" />
            Detected Risk Indicators ({riskIndicators.length})
          </h4>
          <span className="text-xs text-slate-400 font-mono">Deterministic Heuristic Rules</span>
        </div>

        {riskIndicators.length === 0 ? (
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center text-sm text-slate-400">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
            No overt heuristic risk indicators detected in target structure.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {riskIndicators.map((ind, i) => (
              <div 
                key={ind.id || i}
                className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-colors space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-semibold text-white">{ind.name}</span>
                    <RiskBadge severity={ind.severity} size="sm" />
                  </div>
                  <span className="text-xs font-mono text-slate-400">{ind.id}</span>
                </div>
                
                <p className="text-xs text-slate-300 leading-relaxed">{ind.description}</p>
                
                {ind.evidence && (
                  <div className="text-xs font-mono bg-slate-900 px-2.5 py-1 rounded text-cyan-300 border border-slate-800 truncate">
                    <span className="text-slate-400 mr-1">Evidence:</span> {ind.evidence}
                  </div>
                )}

                <div className="text-xs text-slate-400 bg-slate-900/40 p-2 rounded border border-slate-800/50">
                  <span className="text-cyan-400 font-medium">Why it matters:</span> {ind.rationale}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Timestamp & Warning Footer */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-slate-400 font-mono pt-1">
        <span className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          Scanned at: {new Date(timestamp).toLocaleString()}
        </span>
        <span className="text-slate-400">Analysis Engine: Deterministic XAI + Scikit-Learn</span>
      </div>

      {disclaimerOrWarning && (
        <div className="text-xs text-slate-400 leading-relaxed p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/70">
          <span className="text-amber-400 font-semibold font-mono mr-1">Notice:</span> {disclaimerOrWarning}
        </div>
      )}
    </div>
  );
};
