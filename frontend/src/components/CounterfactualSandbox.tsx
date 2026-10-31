import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  RotateCcw, 
  Wand2, 
  ArrowRight,
  Sparkles,
  Info
} from 'lucide-react';
import { simulateCounterfactual } from '../services/api';
import { CounterfactualResult } from '../types';

interface CounterfactualSandboxProps {
  originalUrl: string;
  initialProbability: number;
  initialIsPhishing: boolean;
}

export const CounterfactualSandbox: React.FC<CounterfactualSandboxProps> = ({
  originalUrl,
  initialProbability,
  initialIsPhishing
}) => {
  const [toggles, setToggles] = useState<Record<string, boolean>>({
    force_https: false,
    clean_hostname: false,
    remove_subdomains: false,
    standard_tld: false,
    standard_port: false,
    strip_sensitive_path: false,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CounterfactualResult | null>(null);

  // Auto-run simulation when toggles change
  useEffect(() => {
    const hasAnyActive = Object.values(toggles).some(Boolean);
    if (!hasAnyActive) {
      setResult(null);
      return;
    }

    let active = true;
    setLoading(true);

    const timeout = setTimeout(async () => {
      try {
        const data = await simulateCounterfactual(originalUrl, toggles);
        if (active) {
          setResult(data);
        }
      } catch (err) {
        console.error('Counterfactual simulation error:', err);
      } finally {
        if (active) setLoading(false);
      }
    }, 200);

    return () => {
      active = false;
      clearTimeout(timeout);
    };
  }, [toggles, originalUrl]);

  const handleToggle = (key: string) => {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const applyAll = () => {
    setToggles({
      force_https: true,
      clean_hostname: true,
      remove_subdomains: true,
      standard_tld: true,
      standard_port: true,
      strip_sensitive_path: true,
    });
  };

  const resetAll = () => {
    setToggles({
      force_https: false,
      clean_hostname: false,
      remove_subdomains: false,
      standard_tld: false,
      standard_port: false,
      strip_sensitive_path: false,
    });
    setResult(null);
  };

  const currentProbability = result ? result.counterfactual_probability : initialProbability;
  const currentProbPercent = Math.round(currentProbability * 100);
  const origProbPercent = Math.round(initialProbability * 100);
  const isFlippedToLegit = result?.verdict_flipped && result.counterfactual_prediction === 'Potentially Legitimate';

  const toggleOptions = [
    {
      key: 'force_https',
      label: 'Enforce TLS Encryption (HTTPS)',
      desc: 'Simulates secure certificate handshake and standard port 443.',
      icon: '🔒',
    },
    {
      key: 'clean_hostname',
      label: 'Replace with Legitimate Host (Remove Homoglyphs/IP)',
      desc: 'Eliminates lookalike leetspeak characters, typosquatting, or raw IP addressing.',
      icon: '🧼',
    },
    {
      key: 'remove_subdomains',
      label: 'Strip Subdomain Stacking',
      desc: 'Collapses nested deceptive prefix domains down to root domain.',
      icon: '✂️',
    },
    {
      key: 'standard_tld',
      label: 'Switch to Reputable TLD (.com / .org)',
      desc: 'Removes high-abuse TLDs (.xyz, .top, .buzz) in favor of standard enterprise extensions.',
      icon: '🌐',
    },
    {
      key: 'standard_port',
      label: 'Normalize Port (Remove :8080 / Non-Standard)',
      desc: 'Removes high-risk proxy ports frequently used by phishing kits.',
      icon: '🔌',
    },
    {
      key: 'strip_sensitive_path',
      label: 'Strip Credential Keywords & Query Strings',
      desc: 'Removes tokens like /login, /verify, @ symbols, and tracking parameter payload.',
      icon: '🧹',
    },
  ];

  return (
    <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900/95 via-slate-900/85 to-indigo-950/40 border border-slate-800 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <h3 className="text-base font-bold font-mono text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-indigo-400" />
            "What-If" Counterfactual Simulation Sandbox
          </h3>
          <p className="text-xs text-slate-400">
            Interactive XAI: Toggle hypothetical remediations to watch how feature alterations shift the model's decision boundary.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={applyAll}
            className="px-3 py-1.5 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-700/60 text-indigo-300 text-xs font-mono flex items-center gap-1.5 transition-all"
            title="Simulate all remediations simultaneously"
          >
            <Wand2 className="w-3.5 h-3.5 text-indigo-400" />
            Apply All
          </button>
          <button
            onClick={resetAll}
            className="px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-400 text-xs font-mono flex items-center gap-1.5 transition-all"
            title="Reset sandbox to original URL"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
        </div>
      </div>

      {/* Probability Gauge Comparison */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Baseline Phishing Probability:</span>
            <span className={`font-bold ${initialIsPhishing ? 'text-rose-400' : 'text-emerald-400'}`}>
              {origProbPercent}%
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400">Simulated Probability:</span>
            <span className={`text-sm font-bold ${currentProbPercent >= 50 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {currentProbPercent}%
            </span>
            {result && result.percent_reduction > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-300 text-[11px] font-bold">
                -{result.percent_reduction}% Risk
              </span>
            )}
          </div>
        </div>

        {/* Progress bar comparison */}
        <div className="h-3 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800 relative">
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out ${
              currentProbPercent >= 50
                ? 'bg-gradient-to-r from-amber-500 to-rose-500'
                : 'bg-gradient-to-r from-teal-500 to-emerald-400'
            }`}
            style={{ width: `${Math.max(3, Math.min(100, currentProbPercent))}%` }}
          />
        </div>

        {/* Verdict Flip Callout */}
        {isFlippedToLegit && (
          <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-800/80 text-xs font-mono text-emerald-300 flex items-center gap-2.5 animate-in fade-in">
            <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              <strong>DECISION BOUNDARY CROSSED:</strong> The counterfactual remediations successfully flipped the model verdict to <strong>Potentially Legitimate</strong>!
            </span>
          </div>
        )}
      </div>

      {/* Interactive Toggle Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {toggleOptions.map((opt) => {
          const isActive = toggles[opt.key];
          return (
            <button
              key={opt.key}
              onClick={() => handleToggle(opt.key)}
              className={`p-3.5 rounded-xl border text-left transition-all flex items-start gap-3 select-none ${
                isActive
                  ? 'bg-indigo-950/40 border-indigo-600 shadow-sm shadow-indigo-950'
                  : 'bg-slate-950/60 border-slate-800/90 hover:border-slate-700'
              }`}
            >
              <div className="text-lg mt-0.5">{opt.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className={`text-xs font-mono font-semibold ${isActive ? 'text-indigo-300' : 'text-slate-300'}`}>
                    {opt.label}
                  </span>
                  <div
                    className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-colors ${
                      isActive
                        ? 'bg-indigo-600 border-indigo-500 text-white'
                        : 'border-slate-700 bg-slate-900'
                    }`}
                  >
                    {isActive && <CheckCircle2 className="w-3 h-3" />}
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                  {opt.desc}
                </p>
              </div>
            </button>
          );
        })}
      </div>

      {/* Narrative Output */}
      {result && (
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 leading-relaxed space-y-1">
          <div className="flex items-center gap-1.5 text-indigo-400 font-mono font-semibold">
            <Info className="w-3.5 h-3.5" />
            <span>Simulation Analysis:</span>
          </div>
          <p>{result.narrative}</p>
        </div>
      )}
    </div>
  );
};
