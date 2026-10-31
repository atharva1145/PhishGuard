import React, { useState } from 'react';
import { 
  Layers, 
  Search, 
  Download, 
  FileText, 
  AlertCircle, 
  CheckCircle2, 
  ShieldAlert, 
  ShieldCheck, 
  Copy, 
  Check, 
  Filter, 
  Sparkles,
  Lock
} from 'lucide-react';
import { scanUrlBatch } from '../services/api';
import { BatchUrlScanItem, BatchSummary } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const BulkScannerPage: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<BatchUrlScanItem[]>([]);
  const [summary, setSummary] = useState<BatchSummary | null>(null);
  const [filterRisk, setFilterRisk] = useState<string>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sampleTelemetry = [
    'http://192.168.1.105:8080/secure/paypal/login.php?client_id=98723',
    'http://paypa1.com/cgi-bin/webscr?cmd=_login-run',
    'http://paypal.com.account-verification.login-service.top/auth/signin.html',
    'http://microsoft-verify-support.online-helpdesk.xyz/update-password',
    'https://github.com/torvalds/linux/blob/master/Makefile',
    'https://docs.python.org/3/library/urllib.parse.html',
    'https://apple.com.icloud-security-reset.tk/id/verify',
    'https://en.wikipedia.org/wiki/Phishing',
    'http://amazon-prime-billing-issue.cam/order-update?id=43902',
    'https://developer.mozilla.org/en-US/docs/Web/HTTP'
  ].join('\n');

  const handleScan = async (overrideText?: string) => {
    const raw = (overrideText !== undefined ? overrideText : inputText).trim();
    if (!raw) {
      setError('Please provide at least one URL to scan.');
      return;
    }

    const urls = raw
      .split('\n')
      .map((u) => u.trim())
      .filter((u) => u.length >= 3);

    if (urls.length === 0) {
      setError('No valid URLs found in input.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await scanUrlBatch(urls);
      setResults(data.results);
      setSummary(data.summary);
    } catch (err: any) {
      setError(err.message || 'An error occurred during batch URL triage.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) {
        setInputText(content);
        handleScan(content);
      }
    };
    reader.readAsText(file);
  };

  const copyDefanged = (defanged: string, id: string) => {
    navigator.clipboard.writeText(defanged);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const exportCsv = () => {
    if (results.length === 0) return;

    const headers = [
      'Scan ID',
      'Target URL',
      'Defanged URL',
      'Prediction',
      'Risk Level',
      'Phishing Probability (%)',
      'Detected Brand',
      'Primary Indicator'
    ];

    const rows = results.map((r) => [
      `"${r.scan_id}"`,
      `"${r.target}"`,
      `"${r.defanged_target}"`,
      `"${r.prediction}"`,
      `"${r.risk_level}"`,
      `"${(r.phishing_probability * 100).toFixed(1)}"`,
      `"${r.target_brand || 'None'}"`,
      `"${r.top_indicator || 'None'}"`
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `phishguard-triage-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const filteredResults = results.filter((r) => {
    if (filterRisk === 'all') return true;
    return r.risk_level.toLowerCase() === filterRisk.toLowerCase();
  });

  return (
    <div className="space-y-8 w-full">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2.5">
          <Layers className="w-6 h-6 text-cyan-400" />
          Bulk URL Threat Triage Engine
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Perform concurrent batch analysis on up to 100 URLs exported from proxy alerts, firewall logs, or threat feeds.
        </p>
      </div>

      {/* Input Console */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <label className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider block">
            Target URL List (One URL Per Line)
          </label>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setInputText(sampleTelemetry);
                handleScan(sampleTelemetry);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 hover:border-cyan-700 text-[11px] font-mono text-cyan-400 flex items-center gap-1.5 transition-all"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Load Sample Alert Telemetry (10 URLs)
            </button>
            <label className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 hover:border-cyan-700 text-[11px] font-mono text-slate-300 hover:text-cyan-400 flex items-center gap-1.5 transition-all cursor-pointer">
              <FileText className="w-3.5 h-3.5" />
              Upload .txt / .csv
              <input type="file" accept=".txt,.csv" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
        </div>

        <textarea
          rows={5}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="https://example.com/login&#10;http://192.168.1.1:8080/auth&#10;http://paypa1.com"
          className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-3 text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all resize-y"
        />

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 bg-cyan-950/30 border border-cyan-900/40 px-3 py-1.5 rounded-lg">
            <Lock className="w-3.5 h-3.5 shrink-0" />
            <span>Local Static Sandbox: No outbound network requests are dispatched.</span>
          </div>

          <button
            onClick={() => handleScan()}
            disabled={loading || !inputText.trim()}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-cyan-500 hover:to-teal-400 font-mono font-semibold text-xs text-slate-950 flex items-center justify-center gap-2 transition-all shadow-md shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                Triaging Telemetry...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Run Batch Triage
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-900/60 text-sm text-rose-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Triage Summary Metrics */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 animate-in fade-in">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-[11px] font-mono text-slate-400 uppercase block">Total Scanned</span>
            <span className="text-xl font-bold font-mono text-white mt-1 block">{summary.total}</span>
          </div>
          <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-900/60">
            <span className="text-[11px] font-mono text-rose-400 uppercase block">High Risk (🔴)</span>
            <span className="text-xl font-bold font-mono text-rose-300 mt-1 block">{summary.high_risk}</span>
          </div>
          <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-900/60">
            <span className="text-[11px] font-mono text-amber-400 uppercase block">Medium Risk (🟡)</span>
            <span className="text-xl font-bold font-mono text-amber-300 mt-1 block">{summary.medium_risk}</span>
          </div>
          <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-900/60">
            <span className="text-[11px] font-mono text-emerald-400 uppercase block">Low Risk (🟢)</span>
            <span className="text-xl font-bold font-mono text-emerald-300 mt-1 block">{summary.low_risk}</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-[11px] font-mono text-cyan-400 uppercase block">Phish Ratio</span>
            <span className="text-xl font-bold font-mono text-cyan-300 mt-1 block">
              {summary.total > 0 ? `${Math.round((summary.phishing_count / summary.total) * 100)}%` : '0%'}
            </span>
          </div>
        </div>
      )}

      {/* Triage Table */}
      {results.length > 0 && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl animate-in fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-mono font-semibold text-slate-300 uppercase">Triage Filter:</span>
              <div className="flex items-center gap-1.5">
                {['all', 'high', 'medium', 'low'].map((risk) => (
                  <button
                    key={risk}
                    onClick={() => setFilterRisk(risk)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-mono uppercase transition-all ${
                      filterRisk === risk
                        ? 'bg-cyan-950 border border-cyan-700 text-cyan-300 font-bold'
                        : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {risk}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={exportCsv}
              className="px-3.5 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-700 hover:border-cyan-600 text-xs font-mono font-medium text-cyan-300 flex items-center gap-1.5 transition-all shadow-sm self-start sm:self-auto"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              Export Triage CSV
            </button>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950/80 text-slate-400 uppercase text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Verdict</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Target URL / Defanged IOC</th>
                  <th className="py-3 px-4">Brand Spoofed</th>
                  <th className="py-3 px-4">Primary Indicator</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 bg-slate-950/40">
                {filteredResults.map((r) => (
                  <tr key={r.scan_id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold inline-flex items-center gap-1 ${
                          r.is_phishing
                            ? 'bg-rose-950 border border-rose-800 text-rose-300'
                            : 'bg-emerald-950 border border-emerald-800 text-emerald-300'
                        }`}
                      >
                        {r.is_phishing ? <ShieldAlert className="w-3 h-3" /> : <ShieldCheck className="w-3 h-3" />}
                        {r.prediction}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <RiskBadge severity={r.risk_level.toUpperCase() as any} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {Math.round(r.phishing_probability * 100)}%
                    </td>
                    <td className="py-3 px-4 max-w-xs truncate">
                      <div className="text-white truncate font-medium">{r.target}</div>
                      <div className="text-slate-500 text-[11px] truncate">{r.defanged_target}</div>
                    </td>
                    <td className="py-3 px-4">
                      {r.target_brand ? (
                        <span className="px-2 py-0.5 rounded bg-amber-950 border border-amber-800 text-amber-300 text-[10px] font-bold">
                          {r.target_brand}
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400 truncate max-w-xs">
                      {r.top_indicator || 'Standard structure'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => copyDefanged(r.defanged_target, r.scan_id)}
                        className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-[10px] text-cyan-300 inline-flex items-center gap-1 transition-all"
                        title="Copy defanged safe indicator for Jira / Slack"
                      >
                        {copiedId === r.scan_id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        {copiedId === r.scan_id ? 'Copied' : 'Defang'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <DisclaimerBanner />
    </div>
  );
};
