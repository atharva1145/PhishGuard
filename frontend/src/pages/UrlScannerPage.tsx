import React, { useState } from 'react';
import { 
  Globe, 
  Search, 
  ShieldAlert, 
  ShieldCheck, 
  AlertCircle, 
  Info, 
  CheckCircle2, 
  ArrowRight,
  Lock,
  Layers,
  Sparkles,
  FileText
} from 'lucide-react';
import { scanUrl } from '../services/api';
import { UrlScanResult } from '../types';
import { ExplanationCard } from '../components/ExplanationCard';
import { FeatureImportanceChart } from '../components/FeatureImportanceChart';
import { UrlVisualizer } from '../components/UrlVisualizer';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { downloadForensicReport } from '../utils/forensicReport';

export const UrlScannerPage: React.FC = () => {
  const [urlInput, setUrlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UrlScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const samplePresets = [
    {
      title: 'Homoglyph Lookalike (paypa1.com)',
      url: 'http://paypa1.com/cgi-bin/webscr?cmd=_login-run',
    },
    {
      title: 'Direct IP Host (High Risk)',
      url: 'http://192.168.1.105:8080/secure/paypal/login.php?client_id=98723',
    },
    {
      title: 'Subdomain Spoofing & High-Abuse TLD',
      url: 'http://paypal.com.account-verification.login-service.top/auth/signin.html',
    },
    {
      title: 'Hyphenated Brand Combo-Squatting',
      url: 'http://microsoft-verify-support.online-helpdesk.xyz/update-password',
    },
    {
      title: 'Official GitHub Repository (Legitimate)',
      url: 'https://github.com/torvalds/linux/blob/master/Makefile',
    },
    {
      title: 'Official Python Documentation (Legitimate)',
      url: 'https://docs.python.org/3/library/urllib.parse.html',
    },
  ];

  const handleScan = async (targetUrl?: string) => {
    const toScan = (targetUrl || urlInput).trim();
    if (!toScan) {
      setError('Please provide a URL to analyze.');
      return;
    }
    if (toScan.length < 3) {
      setError('URL must be at least 3 characters.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await scanUrl(toScan);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred during URL scanning.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 w-full">
      {/* Title & Security Promise */}
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2.5">
          <Globe className="w-6 h-6 text-cyan-400" />
          URL Threat Analysis & Explainability
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Deconstructs URL syntax, lexical structure, and host properties to quantify phishing risk without visiting the site.
        </p>
      </div>

      {/* Input Console */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
        <label className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider block">
          Target URL String
        </label>
        
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleScan()}
              placeholder="e.g. https://example.com/login or http://192.168.1.1/auth"
              className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm font-mono text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all"
            />
            {urlInput && (
              <button
                onClick={() => setUrlInput('')}
                className="absolute right-3 top-3 text-xs text-slate-400 hover:text-slate-300 font-mono"
              >
                Clear
              </button>
            )}
          </div>

          <button
            onClick={() => handleScan()}
            disabled={loading || !urlInput.trim()}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-cyan-500 hover:to-teal-400 font-mono font-semibold text-sm text-slate-950 flex items-center justify-center gap-2 transition-all shadow-md shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Analyze URL
              </>
            )}
          </button>
        </div>

        {/* Preset sample buttons */}
        <div className="space-y-2 pt-2">
          <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Quick Demo Presets:
          </span>
          <div className="flex flex-wrap gap-2">
            {samplePresets.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setUrlInput(preset.url);
                  handleScan(preset.url);
                }}
                className="px-2.5 py-1.5 rounded-lg bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-800 text-[11px] font-mono text-slate-300 hover:text-cyan-300 transition-all text-left truncate max-w-xs"
              >
                {preset.title}
              </button>
            ))}
          </div>
        </div>

        {/* Safe Sandbox Assurance */}
        <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 bg-cyan-950/30 border border-cyan-900/40 p-2.5 rounded-lg">
          <Lock className="w-3.5 h-3.5 shrink-0" />
          <span>Security Sandbox: URL is analyzed strictly locally. No outbound packets, DNS requests, or downloads are executed.</span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-900/60 text-sm text-rose-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Analysis Results Display */}
      {result && (
        <div className="space-y-8 animate-in fade-in duration-300">
          <UrlVisualizer tokens={result.syntax_tokens} rawUrl={result.target} />

          {/* Brand Impersonation / Typosquatting Alert Card */}
          {result.brand_impersonation && (
            <div className="p-5 rounded-2xl bg-amber-950/40 border border-amber-800/80 shadow-lg shadow-amber-950/20 space-y-3 animate-in fade-in">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-950 border border-amber-700 flex items-center justify-center text-amber-400 shrink-0">
                    <ShieldAlert className="w-6 h-6 text-amber-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-base font-bold font-mono text-amber-300">
                        Brand Impersonation Detected: {result.brand_impersonation.target_brand}
                      </h4>
                      <span className="px-2 py-0.5 rounded bg-amber-900/60 border border-amber-700 text-amber-200 text-[10px] font-mono uppercase font-bold">
                        {result.brand_impersonation.spoof_technique}
                      </span>
                    </div>
                    <p className="text-xs text-amber-200/80 font-mono mt-0.5">
                      Target Official Domain: <span className="underline font-bold text-white">{result.brand_impersonation.canonical_domain}</span>
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[11px] font-mono text-amber-300 bg-amber-900/50 px-2.5 py-1 rounded-lg border border-amber-700/60">
                    Similarity Match: {(result.brand_impersonation.similarity_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-300 bg-slate-950/70 p-3 rounded-xl border border-slate-800 font-mono leading-relaxed">
                {result.brand_impersonation.details}
              </p>
            </div>
          )}

          {/* Multi-Model Ensemble Consensus */}
          {result.ensemble_consensus && (
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  Multi-Model Ensemble Consensus
                </span>
                <span className="px-2.5 py-1 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-300 font-bold text-[11px]">
                  {result.ensemble_consensus.consensus_verdict}
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                {result.ensemble_consensus.models.map((m, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs font-mono">
                    <div>
                      <span className="text-white font-medium block">{m.model_name}</span>
                      <span className="text-slate-400 text-[11px]">Prob: {(m.phishing_probability * 100).toFixed(1)}%</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      m.is_phishing 
                        ? 'bg-rose-950 border border-rose-800 text-rose-400' 
                        : 'bg-emerald-950 border border-emerald-800 text-emerald-400'
                    }`}>
                      {m.prediction}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <ExplanationCard
            prediction={result.prediction}
            isPhishing={result.is_phishing}
            confidenceScore={result.confidence_score}
            phishingProbability={result.phishing_probability}
            riskLevel={result.risk_level}
            explanation={result.explanation}
            riskIndicators={result.risk_indicators}
            modelVersion={result.model_version}
            timestamp={result.timestamp}
            disclaimerOrWarning={result.disclaimer}
            onExportReport={() => downloadForensicReport(result)}
          />

          <FeatureImportanceChart
            features={result.feature_contributions}
            title="Structural URL Feature Attributions"
            subtitle="Logistic regression mathematical weights multiplied by normalized feature values."
          />
        </div>
      )}

      <DisclaimerBanner />
    </div>
  );
};
