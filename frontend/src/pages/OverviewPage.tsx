import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  Globe, 
  Mail, 
  ShieldAlert, 
  ShieldCheck, 
  BarChart3, 
  ArrowRight, 
  AlertCircle,
  RefreshCw,
  Clock
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { RiskBadge } from '../components/RiskBadge';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { AllMetricsData, HistoryItem } from '../types';
import { getMetrics, getHistory } from '../services/api';

interface OverviewPageProps {
  setActiveTab: (tab: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ setActiveTab }) => {
  const [metricsData, setMetricsData] = useState<AllMetricsData | null>(null);
  const [recentHistory, setRecentHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [m, h] = await Promise.all([
        getMetrics(),
        getHistory({ limit: 5 })
      ]);
      setMetricsData(m);
      setRecentHistory(h.items);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const stats = metricsData?.scan_statistics || {
    total_scans: 0,
    phishing_scans: 0,
    legitimate_scans: 0,
    url_scans: 0,
    email_scans: 0,
    phishing_ratio: 0
  };

  const urlEval = metricsData?.url_evaluation;
  const emailEval = metricsData?.email_evaluation;

  return (
    <div className="space-y-8 w-full">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-cyan-950/40 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2.5">
            <Activity className="w-6 h-6 text-cyan-400" />
            Security Intelligence Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time explainable phishing detection for suspicious URLs and deceptive emails.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="self-start md:self-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 hover:border-cyan-500/40 text-xs font-mono text-slate-300 hover:text-white transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          Refresh Telemetry
        </button>
      </div>

      <DisclaimerBanner />

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-900/60 text-sm text-rose-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <p>{error} Ensure the backend server is running on port 8000.</p>
        </div>
      )}

      {/* 4 Primary Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Scans Logged"
          value={stats.total_scans}
          subtitle={`${stats.url_scans} URLs • ${stats.email_scans} Emails analyzed`}
          icon={Activity}
          variant="cyan"
        />
        <MetricCard
          label="Threat Detection Ratio"
          value={`${(stats.phishing_ratio * 100).toFixed(1)}%`}
          subtitle={`${stats.phishing_scans} Flagged suspicious • ${stats.legitimate_scans} Legitimate`}
          icon={ShieldAlert}
          variant={stats.phishing_ratio > 0.5 ? 'rose' : 'teal'}
        />
        <MetricCard
          label="URL Model F1-Score"
          value={urlEval ? `${(urlEval.metrics.f1_score * 100).toFixed(1)}%` : 'Active'}
          subtitle={urlEval ? `FPR: ${(urlEval.metrics.false_positive_rate! * 100).toFixed(1)}% on held-out test` : 'Logistic Regression'}
          icon={Globe}
          variant="cyan"
        />
        <MetricCard
          label="Email NLP F1-Score"
          value={emailEval ? `${(emailEval.metrics.f1_score * 100).toFixed(1)}%` : 'Active'}
          subtitle={emailEval ? `FPR: ${(emailEval.metrics.false_positive_rate! * 100).toFixed(1)}% on held-out test` : 'TF-IDF + LogReg'}
          icon={Mail}
          variant="teal"
        />
      </div>

      {/* Quick Launch Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div 
          onClick={() => setActiveTab('url')}
          className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 cursor-pointer transition-all group relative overflow-hidden"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-cyan-950/60 border border-cyan-800 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform">
              <Globe className="w-6 h-6" />
            </div>
            <span className="flex items-center gap-1 text-xs font-mono text-cyan-400 group-hover:translate-x-1 transition-transform">
              Launch Scanner <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </div>
          <h3 className="text-lg font-bold font-mono text-white mb-1">URL Threat Scanner</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Local structural and lexical feature analysis without visiting the target. Identifies IP hosts, punycode homographs, credential traps, and brand impersonation.
          </p>
        </div>

        <div 
          onClick={() => setActiveTab('email')}
          className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-teal-500/50 cursor-pointer transition-all group relative overflow-hidden"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-teal-950/60 border border-teal-800 flex items-center justify-center text-teal-400 group-hover:scale-105 transition-transform">
              <Mail className="w-6 h-6" />
            </div>
            <span className="flex items-center gap-1 text-xs font-mono text-teal-400 group-hover:translate-x-1 transition-transform">
              Launch Scanner <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </div>
          <h3 className="text-lg font-bold font-mono text-white mb-1">Email NLP Scanner</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Analyzes subject line and email body text via TF-IDF n-grams to detect psychological urgency, credential harvesting, wire fraud, and suspicious call-to-actions.
          </p>
        </div>
      </div>

      {/* Model Performance Snapshot */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            Active Model Test Set Evaluation
          </h3>
          <button
            onClick={() => setActiveTab('evaluation')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1"
          >
            Full Evaluation Reports <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* URL Classifier Card */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <div className="flex items-center gap-2 font-mono text-sm font-semibold text-slate-200">
                <Globe className="w-4 h-4 text-cyan-400" />
                URL Classifier
              </div>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800 text-cyan-400">
                {urlEval?.model_version || 'v1.0.0'}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center font-mono">
              <div className="p-2 rounded bg-slate-900 border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase block">Accuracy</span>
                <span className="text-sm font-bold text-white">
                  {urlEval ? `${(urlEval.metrics.accuracy * 100).toFixed(1)}%` : '--'}
                </span>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase block">Precision</span>
                <span className="text-sm font-bold text-white">
                  {urlEval ? `${(urlEval.metrics.precision * 100).toFixed(1)}%` : '--'}
                </span>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase block">Recall</span>
                <span className="text-sm font-bold text-white">
                  {urlEval ? `${(urlEval.metrics.recall * 100).toFixed(1)}%` : '--'}
                </span>
              </div>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Fitted on {urlEval?.dataset_summary.train_records ?? 0} samples; evaluated on {urlEval?.dataset_summary.test_records ?? 0} held-out samples.
            </p>
          </div>

          {/* Email Classifier Card */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <div className="flex items-center gap-2 font-mono text-sm font-semibold text-slate-200">
                <Mail className="w-4 h-4 text-teal-400" />
                Email NLP Classifier
              </div>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-teal-950/60 border border-teal-800 text-teal-400">
                {emailEval?.model_version || 'v1.0.0'}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center font-mono">
              <div className="p-2 rounded bg-slate-900 border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase block">Accuracy</span>
                <span className="text-sm font-bold text-white">
                  {emailEval ? `${(emailEval.metrics.accuracy * 100).toFixed(1)}%` : '--'}
                </span>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase block">Precision</span>
                <span className="text-sm font-bold text-white">
                  {emailEval ? `${(emailEval.metrics.precision * 100).toFixed(1)}%` : '--'}
                </span>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase block">Recall</span>
                <span className="text-sm font-bold text-white">
                  {emailEval ? `${(emailEval.metrics.recall * 100).toFixed(1)}%` : '--'}
                </span>
              </div>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Fitted on {emailEval?.dataset_summary.train_records ?? 0} samples; evaluated on {emailEval?.dataset_summary.test_records ?? 0} held-out samples.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Scan History Feed */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            Recent Scans
          </h3>
          <button
            onClick={() => setActiveTab('history')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1"
          >
            View Complete History <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        {recentHistory.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-950/60 border border-slate-800 text-center space-y-2">
            <p className="text-sm text-slate-400">No scans logged in history yet.</p>
            <p className="text-xs text-slate-400">Run a URL or Email scan to generate analysis records.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase">
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Target Preview</th>
                  <th className="py-2.5 px-3">Prediction</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentHistory.map((item) => (
                  <tr key={item.scan_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-3 uppercase text-cyan-400">
                      {item.scan_type}
                    </td>
                    <td className="py-2.5 px-3 text-slate-200 max-w-xs truncate">
                      {item.target_preview}
                    </td>
                    <td className="py-2.5 px-3">
                      <RiskBadge prediction={item.prediction} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 text-slate-300">
                      {Math.round(item.confidence_score * 100)}%
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">
                      {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
