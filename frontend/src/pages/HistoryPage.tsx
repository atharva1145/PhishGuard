import React, { useEffect, useState } from 'react';
import { 
  History, 
  Search, 
  Trash2, 
  Filter, 
  RefreshCw, 
  Eye, 
  AlertCircle, 
  Globe, 
  Mail, 
  Clock, 
  X,
  AlertTriangle,
  CheckCircle2,
  FileText
} from 'lucide-react';
import { getHistory, deleteHistoryItem, clearAllHistory } from '../services/api';
import { HistoryItem } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { downloadHistoryForensicReport } from '../utils/forensicReport';

export const HistoryPage: React.FC = () => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [scanType, setScanType] = useState<string>('all');
  const [prediction, setPrediction] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Modals
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null);
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getHistory({
        scan_type: scanType,
        prediction: prediction,
        search: searchTerm,
        limit: 100,
      });
      setItems(res.items);
      setTotal(res.total);
    } catch (err: any) {
      setError(err.message || 'Failed to load scan history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [scanType, prediction]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleDeleteItem = async (scanId: string) => {
    try {
      await deleteHistoryItem(scanId);
      setItems((prev) => prev.filter((it) => it.scan_id !== scanId));
      setTotal((prev) => Math.max(0, prev - 1));
      if (selectedItem?.scan_id === scanId) {
        setSelectedItem(null);
      }
    } catch (err: any) {
      alert(`Failed to delete record: ${err.message}`);
    }
  };

  const handleClearAll = async () => {
    try {
      await clearAllHistory();
      setItems([]);
      setTotal(0);
      setShowClearConfirm(false);
      setSelectedItem(null);
    } catch (err: any) {
      alert(`Failed to clear history: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-cyan-950/40 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2.5">
            <History className="w-6 h-6 text-cyan-400" />
            Audit Scan History
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Persisted records of past scans stored locally in SQLite with privacy-preserving metadata.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchHistory}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 hover:border-cyan-500/40 text-xs font-mono text-slate-300 hover:text-white transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            Refresh
          </button>

          {items.length > 0 && (
            <button
              onClick={() => setShowClearConfirm(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-rose-950/40 border border-rose-900/60 hover:bg-rose-900/50 text-xs font-mono text-rose-300 transition-all"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear All History
            </button>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search target preview..."
              className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2 text-xs font-mono text-white placeholder-slate-400 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 transition-all"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Scan Type Filter */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="text-slate-400">Type:</span>
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs font-mono text-slate-200 focus:outline-none"
            >
              <option value="all">All Types</option>
              <option value="url">URL</option>
              <option value="email">Email</option>
            </select>
          </div>

          {/* Prediction Filter */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="text-slate-400">Prediction:</span>
            <select
              value={prediction}
              onChange={(e) => setPrediction(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs font-mono text-slate-200 focus:outline-none"
            >
              <option value="all">All Verdicts</option>
              <option value="phishing">Phishing</option>
              <option value="legitimate">Legitimate</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-900/60 text-sm text-rose-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* History Table */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Total Records: {total}</span>
          <span>Displaying latest {items.length} entries</span>
        </div>

        {items.length === 0 ? (
          <div className="p-12 rounded-xl bg-slate-950/60 border border-slate-800 text-center space-y-2">
            <p className="text-sm font-mono text-slate-400">No scan records found matching filters.</p>
            <p className="text-xs text-slate-400">Run a scan on the URL or Email Scanner page to record telemetry.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase">
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Target Preview</th>
                  <th className="py-3 px-3">Prediction</th>
                  <th className="py-3 px-3">Confidence</th>
                  <th className="py-3 px-3">Risk Level</th>
                  <th className="py-3 px-3">Indicators</th>
                  <th className="py-3 px-3">Timestamp</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {items.map((it) => (
                  <tr key={it.scan_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 font-semibold uppercase text-cyan-400 flex items-center gap-1.5">
                      {it.scan_type === 'url' ? <Globe className="w-3.5 h-3.5" /> : <Mail className="w-3.5 h-3.5 text-teal-400" />}
                      {it.scan_type}
                    </td>
                    <td className="py-3 px-3 text-slate-200 max-w-xs truncate">
                      {it.target_preview}
                    </td>
                    <td className="py-3 px-3">
                      <RiskBadge prediction={it.prediction} size="sm" />
                    </td>
                    <td className="py-3 px-3 text-slate-200">
                      {Math.round(it.confidence_score * 100)}%
                    </td>
                    <td className="py-3 px-3">
                      <RiskBadge severity={it.risk_level.toUpperCase() as any} size="sm" />
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {it.indicators_count} signals
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {new Date(it.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setSelectedItem(it)}
                          className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-300 transition-colors"
                          title="View Analysis Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteItem(it.scan_id)}
                          className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 hover:border-rose-500/50 text-slate-300 hover:text-rose-400 transition-colors"
                          title="Delete Record"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 font-mono">
                <span className="text-sm font-bold text-white uppercase">{selectedItem.scan_type} Scan Details</span>
                <RiskBadge prediction={selectedItem.prediction} size="sm" />
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-slate-400 uppercase text-[10px] block">Target Preview:</span>
                <span className="text-slate-200 break-all">{selectedItem.target_preview}</span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-400 uppercase text-[10px] block">Scan ID:</span>
                  <span className="text-slate-300 truncate block">{selectedItem.scan_id}</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-400 uppercase text-[10px] block">Model Version:</span>
                  <span className="text-cyan-400">{selectedItem.model_version}</span>
                </div>
              </div>

              {selectedItem.details?.explanation && (
                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 text-slate-200 font-sans leading-relaxed">
                  <span className="font-semibold text-cyan-400 font-mono block mb-1">Stored Explanation:</span>
                  {selectedItem.details.explanation}
                </div>
              )}

              {/* Stored Risk Indicators */}
              {selectedItem.details?.risk_indicators && selectedItem.details.risk_indicators.length > 0 && (
                <div className="space-y-2">
                  <span className="text-slate-400 uppercase text-[10px] block">Logged Risk Indicators:</span>
                  {selectedItem.details.risk_indicators.map((ind, i) => (
                    <div key={i} className="p-2.5 rounded bg-slate-950 border border-slate-800 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white">{ind.name}</span>
                        <RiskBadge severity={ind.severity} size="sm" />
                      </div>
                      <p className="text-slate-400 font-sans text-[11px]">{ind.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-800">
              <button
                onClick={() => selectedItem && downloadHistoryForensicReport(selectedItem)}
                className="px-3.5 py-2 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-700 hover:border-cyan-600 text-xs font-mono font-medium text-cyan-300 flex items-center gap-1.5 transition-colors"
                title="Download forensic incident report (.txt)"
              >
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                Export Incident Report
              </button>
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono text-white transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Clear All Confirmation Modal */}
      {showClearConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-slate-900 border border-rose-900/60 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-rose-400">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="text-lg font-bold font-mono">Confirm History Deletion</h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">
              Are you sure you want to delete all local scan history records? This action cannot be undone.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowClearConfirm(false)}
                className="px-4 py-2 rounded-xl border border-slate-800 text-xs font-mono text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleClearAll}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-mono font-semibold text-white transition-all shadow-md shadow-rose-950"
              >
                Delete All Records
              </button>
            </div>
          </div>
        </div>
      )}

      <DisclaimerBanner />
    </div>
  );
};
