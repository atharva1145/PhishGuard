import React from 'react';
import { AlertTriangle, ShieldCheck, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface ConfusionMatrixProps {
  matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
    matrix_2x2: number[][];
  };
  fpr: number | null;
  fnr: number | null;
}

export const ConfusionMatrix: React.FC<ConfusionMatrixProps> = ({ matrix, fpr, fnr }) => {
  const { true_negatives, false_positives, false_negatives, true_positives } = matrix;
  const total = true_negatives + false_positives + false_negatives + true_positives;

  const fprText = fpr !== null ? `${(fpr * 100).toFixed(2)}%` : 'N/A';
  const fnrText = fnr !== null ? `${(fnr * 100).toFixed(2)}%` : 'N/A';

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200">
            Confusion Matrix (Held-Out Test Set)
          </h4>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluated on N = {total} unseen samples strictly isolated prior to model fitting.
          </p>
        </div>
        <div className="flex gap-4 font-mono text-xs">
          <div className="px-2.5 py-1 rounded bg-slate-950 border border-slate-800">
            <span className="text-slate-400">FPR:</span>{' '}
            <span className="font-semibold text-amber-400">{fprText}</span>
          </div>
          <div className="px-2.5 py-1 rounded bg-slate-950 border border-slate-800">
            <span className="text-slate-400">FNR:</span>{' '}
            <span className="font-semibold text-rose-400">{fnrText}</span>
          </div>
        </div>
      </div>

      {/* 2x2 Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* True Negatives */}
        <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/40 relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-medium text-emerald-400 uppercase">
              True Negatives (TN)
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-emerald-300">
            {true_negatives}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Actual: Legitimate → Predicted: Legitimate
          </p>
        </div>

        {/* False Positives */}
        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-900/40 relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-medium text-amber-400 uppercase">
              False Positives (FP)
            </span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-amber-300">
            {false_positives}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Actual: Legitimate → Predicted: Phishing
          </p>
        </div>

        {/* False Negatives */}
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-900/40 relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-medium text-rose-400 uppercase">
              False Negatives (FN)
            </span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-rose-300">
            {false_negatives}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Actual: Phishing → Predicted: Legitimate
          </p>
        </div>

        {/* True Positives */}
        <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-900/40 relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-medium text-cyan-400 uppercase">
              True Positives (TP)
            </span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-cyan-300">
            {true_positives}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Actual: Phishing → Predicted: Phishing
          </p>
        </div>
      </div>

      {/* Metric Explanations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans text-slate-400 pt-2 border-t border-slate-800/80">
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 space-y-1">
          <span className="font-semibold text-amber-400 font-mono">Why False Positives Matter:</span>
          <p className="leading-relaxed">
            FPR = FP / (FP + TN). A high false positive rate flags authentic customer emails or legitimate enterprise portals, causing alert fatigue, lost productivity, and blocked business transactions.
          </p>
        </div>
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 space-y-1">
          <span className="font-semibold text-rose-400 font-mono">Why False Negatives Matter:</span>
          <p className="leading-relaxed">
            FNR = FN / (FN + TP). A high false negative rate means sophisticated phishing payloads bypass security controls, presenting severe danger of account takeover, credential exfiltration, and ransomware.
          </p>
        </div>
      </div>
    </div>
  );
};
