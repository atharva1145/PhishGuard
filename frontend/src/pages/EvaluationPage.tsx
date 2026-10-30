import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  Globe, 
  Mail, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Cpu, 
  Calendar,
  Layers,
  ArrowRight,
  Database,
  RefreshCw,
  Search,
  AlertCircle
} from 'lucide-react';
import { getMetrics } from '../services/api';
import { AllMetricsData, EvaluationReport, MisclassifiedSample } from '../types';
import { ConfusionMatrix } from '../components/ConfusionMatrix';
import { MetricCard } from '../components/MetricCard';
import { RiskBadge } from '../components/RiskBadge';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const EvaluationPage: React.FC = () => {
  const [metricsData, setMetricsData] = useState<AllMetricsData | null>(null);
  const [selectedModel, setSelectedModel] = useState<'url' | 'email'>('url');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterMisclassified, setFilterMisclassified] = useState<string>('all');

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMetrics();
      setMetricsData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load model evaluation reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const currentReport: EvaluationReport | null = 
    selectedModel === 'url' ? metricsData?.url_evaluation || null : metricsData?.email_evaluation || null;

  return (
    <div className="space-y-8 w-full">
      {/* Title & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-cyan-950/40 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2.5">
            <BarChart3 className="w-6 h-6 text-cyan-400" />
            Model Evaluation & Generalization Benchmarks
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Strict empirical test-set metrics generated strictly after train/test separation with asserted zero leakage.
          </p>
        </div>

        <button
          onClick={fetchMetrics}
          disabled={loading}
          className="self-start md:self-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 hover:border-cyan-500/40 text-xs font-mono text-slate-300 hover:text-white transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          Reload Reports
        </button>
      </div>

      {/* Model Selector Tabs */}
      <div className="flex gap-3 border-b border-slate-800 pb-3">
        <button
          onClick={() => setSelectedModel('url')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-mono transition-all ${
            selectedModel === 'url'
              ? 'bg-cyan-950/80 border border-cyan-800 text-cyan-300 font-semibold shadow-md shadow-cyan-950/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <Globe className="w-4 h-4" />
          URL Classifier (Lexical Features)
        </button>

        <button
          onClick={() => setSelectedModel('email')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-mono transition-all ${
            selectedModel === 'email'
              ? 'bg-teal-950/80 border border-teal-800 text-teal-300 font-semibold shadow-md shadow-teal-950/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <Mail className="w-4 h-4" />
          Email NLP Classifier (TF-IDF)
        </button>
      </div>

      {!currentReport && !loading && (
        <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
          <h3 className="text-lg font-bold font-mono text-white">No Evaluation Report Found</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Model evaluation artifacts have not been generated yet. Please execute the training script:
            <code className="block mt-2 p-2 rounded bg-slate-950 text-cyan-400 font-mono text-xs">
              python scripts/train_models.py
            </code>
          </p>
        </div>
      )}

      {currentReport && (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* Metadata Card */}
          <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-400">Algorithm:</span>
              <span className="font-semibold text-slate-200">{currentReport.algorithm}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Version:</span>
              <span className="text-cyan-400 font-semibold">{currentReport.model_version}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-slate-400" />
              <span className="text-slate-400">Evaluated At:</span>
              <span className="text-slate-200">{new Date(currentReport.evaluated_at).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-slate-400" />
              <span className="text-slate-400">Dataset Size:</span>
              <span className="text-slate-200">{currentReport.dataset_summary.total_records} records</span>
            </div>
          </div>

          {/* 6 Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <MetricCard
              label="Accuracy"
              value={`${(currentReport.metrics.accuracy * 100).toFixed(1)}%`}
              subtitle="Overall correct predictions"
              icon={CheckCircle2}
              variant="cyan"
            />
            <MetricCard
              label="Precision"
              value={`${(currentReport.metrics.precision * 100).toFixed(1)}%`}
              subtitle="TP / (TP + FP)"
              icon={BarChart3}
              variant="teal"
            />
            <MetricCard
              label="Recall"
              value={`${(currentReport.metrics.recall * 100).toFixed(1)}%`}
              subtitle="TP / (TP + FN)"
              icon={BarChart3}
              variant="teal"
            />
            <MetricCard
              label="F1-Score"
              value={(currentReport.metrics.f1_score).toFixed(4)}
              subtitle="Harmonic mean of P & R"
              icon={BarChart3}
              variant="cyan"
            />
            <MetricCard
              label="False-Pos Rate"
              value={currentReport.metrics.false_positive_rate !== null ? `${(currentReport.metrics.false_positive_rate * 100).toFixed(1)}%` : 'N/A'}
              subtitle="FP / (FP + TN)"
              icon={AlertTriangle}
              variant="amber"
            />
            <MetricCard
              label="False-Neg Rate"
              value={currentReport.metrics.false_negative_rate !== null ? `${(currentReport.metrics.false_negative_rate * 100).toFixed(1)}%` : 'N/A'}
              subtitle="FN / (FN + TP)"
              icon={ShieldAlert}
              variant="rose"
            />
          </div>

          {/* Confusion Matrix Visualization */}
          <ConfusionMatrix
            matrix={currentReport.metrics.confusion_matrix}
            fpr={currentReport.metrics.false_positive_rate}
            fnr={currentReport.metrics.false_negative_rate}
          />

          {/* Per-Class Metrics & Split Distribution */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Per-class breakdown table */}
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
              <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200">
                Per-Class Performance Breakdown
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase">
                      <th className="py-2 px-3">Class</th>
                      <th className="py-2 px-3">Precision</th>
                      <th className="py-2 px-3">Recall</th>
                      <th className="py-2 px-3">F1-Score</th>
                      <th className="py-2 px-3">Support</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    <tr>
                      <td className="py-2.5 px-3 font-semibold text-emerald-400">Legitimate (0)</td>
                      <td className="py-2.5 px-3 text-slate-200">
                        {(currentReport.metrics.per_class.legitimate.precision * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3 text-slate-200">
                        {(currentReport.metrics.per_class.legitimate.recall * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3 text-slate-200">
                        {currentReport.metrics.per_class.legitimate.f1_score.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">
                        {currentReport.metrics.per_class.legitimate.support}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-3 font-semibold text-rose-400">Phishing (1)</td>
                      <td className="py-2.5 px-3 text-slate-200">
                        {(currentReport.metrics.per_class.phishing.precision * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3 text-slate-200">
                        {(currentReport.metrics.per_class.phishing.recall * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3 text-slate-200">
                        {currentReport.metrics.per_class.phishing.f1_score.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">
                        {currentReport.metrics.per_class.phishing.support}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Split and Dataset Statistics */}
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
              <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200">
                Split Distribution & Integrity
              </h4>
              <div className="space-y-3 text-xs font-mono">
                <div className="flex justify-between p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Training Split (80%):</span>
                  <span className="text-slate-200 font-semibold">
                    {currentReport.dataset_summary.train_records} samples 
                    ({currentReport.dataset_summary.class_distribution.train_phishing} Phish / {currentReport.dataset_summary.class_distribution.train_legitimate} Legit)
                  </span>
                </div>
                <div className="flex justify-between p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Held-Out Test Split (20%):</span>
                  <span className="text-slate-200 font-semibold">
                    {currentReport.dataset_summary.test_records} samples 
                    ({currentReport.dataset_summary.class_distribution.test_phishing} Phish / {currentReport.dataset_summary.class_distribution.test_legitimate} Legit)
                  </span>
                </div>
                <div className="p-3 rounded bg-slate-950/80 border border-slate-800 text-[11px] text-slate-400 font-sans leading-relaxed">
                  <span className="text-cyan-400 font-mono font-semibold">Leakage Control Protocol: </span>
                  {currentReport.evaluation_protocol}
                </div>
              </div>
            </div>
          </div>

          {/* Model Comparison Table */}
          {currentReport.model_comparison && currentReport.model_comparison.length > 0 && (
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  Algorithm Comparison (5-Fold Stratified Cross-Validation on Training Data)
                </h4>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase">
                      <th className="py-2.5 px-3">Candidate Model</th>
                      <th className="py-2.5 px-3">CV Accuracy</th>
                      <th className="py-2.5 px-3">CV Precision</th>
                      <th className="py-2.5 px-3">CV Recall</th>
                      <th className="py-2.5 px-3">CV F1-Score</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {currentReport.model_comparison.map((candidate, idx) => (
                      <tr key={idx} className={candidate.selected ? 'bg-cyan-950/20' : ''}>
                        <td className="py-2.5 px-3 font-semibold text-slate-200">
                          {candidate.model_name}
                        </td>
                        <td className="py-2.5 px-3 text-slate-300">
                          {(candidate.cv_accuracy * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 text-slate-300">
                          {(candidate.cv_precision * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 text-slate-300">
                          {(candidate.cv_recall * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 text-slate-300 font-bold">
                          {candidate.cv_f1.toFixed(4)}
                        </td>
                        <td className="py-2.5 px-3">
                          {candidate.selected ? (
                            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-400">
                              Selected Model
                            </span>
                          ) : (
                            <span className="text-[10px] text-slate-400 uppercase">
                              Evaluated Alternative
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Misclassified Samples Inspection (Safe Sanitized Representation) */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200 flex items-center gap-2">
                  <Search className="w-4 h-4 text-cyan-400" />
                  Test Set Error Inspection (Sanitized Samples)
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Inspect false positives and false negatives to diagnose edge-case decision boundaries.
                </p>
              </div>
            </div>

            {(!currentReport.misclassified_samples || currentReport.misclassified_samples.length === 0) ? (
              <div className="p-8 rounded-xl bg-slate-950/60 border border-slate-800 text-center space-y-2">
                <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto" />
                <p className="text-sm font-mono text-emerald-400 font-semibold">
                  Zero Misclassifications on Held-Out Test Set
                </p>
                <p className="text-xs text-slate-400">
                  The model achieved 100% test split separation on the evaluated benchmark test partition.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {currentReport.misclassified_samples.map((item, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 font-mono text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 truncate max-w-lg">{item.preview}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${
                        item.error_type === 'False Positive' 
                          ? 'bg-amber-950/80 border-amber-800 text-amber-300' 
                          : 'bg-rose-950/80 border-rose-800 text-rose-300'
                      }`}>
                        {item.error_type}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-slate-400">
                      <span>Actual: <b className="text-white">{item.true_label_name}</b></span>
                      <span>Predicted: <b className="text-cyan-400">{item.predicted_label_name}</b></span>
                      <span>Score: <b className="text-slate-200">{(item.predicted_score * 100).toFixed(1)}%</b></span>
                    </div>
                    <p className="text-slate-400 font-sans text-xs pt-1 border-t border-slate-900">
                      {item.reason_notes}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <DisclaimerBanner />
    </div>
  );
};
