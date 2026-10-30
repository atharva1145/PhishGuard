import React from 'react';
import { AlertCircle } from 'lucide-react';

interface DisclaimerBannerProps {
  message?: string;
}

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({ message }) => {
  return (
    <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-4 text-xs text-slate-400 flex items-start gap-3">
      <AlertCircle className="w-4 h-4 text-cyan-400 mt-0.5 shrink-0" />
      <div className="space-y-1">
        <p className="font-semibold text-slate-300">Defensive Analysis Disclaimer</p>
        <p className="leading-relaxed">
          {message || (
            "PhishGuard predictions are probabilistic estimates based on engineered string syntax, lexical signals, and natural language tokens. " +
            "Predictions are defensive indicators and can occasionally yield false positives or false negatives. " +
            "PhishGuard never executes or visits scanned URLs and does not claim to verify cryptographic email transport headers (SPF, DKIM, DMARC)."
          )}
        </p>
      </div>
    </div>
  );
};
