import React, { useState } from 'react';
import { Shield, Copy, Check, ArrowRightLeft, Lock } from 'lucide-react';
import { defangIndicator } from '../services/api';

interface UrlDefangerCardProps {
  currentUrl?: string;
  currentDefanged?: string;
}

export const UrlDefangerCard: React.FC<UrlDefangerCardProps> = ({ currentUrl, currentDefanged }) => {
  const [inputVal, setInputVal] = useState(currentUrl || '');
  const [outputVal, setOutputVal] = useState(currentDefanged || '');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (currentUrl) setInputVal(currentUrl);
    if (currentDefanged) setOutputVal(currentDefanged);
  }, [currentUrl, currentDefanged]);

  const handleAction = async (action: 'defang' | 'refang') => {
    if (!inputVal.trim()) return;
    try {
      setLoading(true);
      const res = await defangIndicator(inputVal, action);
      if (action === 'defang') {
        setOutputVal(res.defanged_url);
      } else {
        setOutputVal(res.raw_url);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!outputVal) return;
    navigator.clipboard.writeText(outputVal);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <Shield className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold font-mono text-white">
            SOC Indicator Defanging & Safe Link Utility
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          Replaces <code className="text-cyan-400">http://</code> with <code className="text-cyan-400">hxxp://</code> and <code className="text-cyan-400">.</code> with <code className="text-cyan-400">[.]</code>
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Input */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-mono text-slate-400 block">Input URL or Indicator</label>
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="e.g. http://paypa1.com/login"
            className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none"
          />
        </div>

        {/* Output */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="text-[11px] font-mono text-slate-400 block">Safe Defanged String</label>
            {outputVal && (
              <button
                onClick={copyToClipboard}
                className="text-[11px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            )}
          </div>
          <div className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-cyan-300 min-h-[34px] flex items-center overflow-x-auto truncate">
            {outputVal || <span className="text-slate-500">Output will appear here...</span>}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end gap-2 pt-1">
        <button
          onClick={() => handleAction('defang')}
          disabled={loading || !inputVal.trim()}
          className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-mono font-bold transition-all disabled:opacity-50"
        >
          Defang Link (Safe)
        </button>
        <button
          onClick={() => handleAction('refang')}
          disabled={loading || !inputVal.trim()}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-mono font-bold transition-all disabled:opacity-50 flex items-center gap-1"
        >
          <ArrowRightLeft className="w-3 h-3" />
          Refang (Restore)
        </button>
      </div>
    </div>
  );
};
