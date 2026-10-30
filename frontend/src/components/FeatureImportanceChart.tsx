import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { FeatureContribution, InfluentialTerm } from '../types';
import { HelpCircle } from 'lucide-react';

interface FeatureImportanceChartProps {
  features?: FeatureContribution[];
  terms?: InfluentialTerm[];
  title?: string;
  subtitle?: string;
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({
  features,
  terms,
  title = "Feature Influence on Decision Boundary",
  subtitle = "Exact log-odds mathematical contributions: positive values push toward Phishing; negative values push toward Legitimate."
}) => {
  // Format data for chart
  const data = (features || []).map((f) => ({
    name: f.display_name,
    rawName: f.feature,
    contribution: f.contribution,
    direction: f.direction,
    rawValue: f.raw_value,
    description: f.description,
  })).concat(
    (terms || []).map((t) => ({
      name: `"${t.term}"`,
      rawName: t.term,
      contribution: t.contribution,
      direction: t.direction,
      rawValue: `TF-IDF: ${t.tfidf_value}`,
      description: `Logistic Regression coefficient: ${t.coefficient}`,
    }))
  );

  if (data.length === 0) {
    return (
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 text-center text-sm text-slate-400">
        No feature contribution data available for this prediction.
      </div>
    );
  }

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
      <div>
        <h4 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200">
          {title}
        </h4>
        <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
          {subtitle}
        </p>
      </div>

      <div className="space-y-3 pt-2">
        {data.map((item, idx) => {
          const isPhish = item.direction === 'phishing';
          const absVal = Math.abs(item.contribution);
          const maxContrib = Math.max(...data.map(d => Math.abs(d.contribution)), 0.01);
          const percentWidth = Math.min(100, Math.round((absVal / maxContrib) * 100));

          return (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5 font-mono">
                  <span className="font-medium text-slate-200">{item.name}</span>
                  {item.rawValue !== undefined && (
                    <span className="text-slate-400 text-[11px]">({item.rawValue})</span>
                  )}
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className={`font-semibold ${isPhish ? 'text-rose-400' : 'text-teal-400'}`}>
                    {item.contribution > 0 ? `+${item.contribution}` : item.contribution}
                  </span>
                  <span className={`text-[10px] uppercase px-1.5 py-0.2 rounded border ${
                    isPhish 
                      ? 'bg-rose-950/60 border-rose-800/80 text-rose-300' 
                      : 'bg-teal-950/60 border-teal-800/80 text-teal-300'
                  }`}>
                    {item.direction}
                  </span>
                </div>
              </div>

              {/* Two-way visual bar */}
              <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden flex items-center border border-slate-800/80">
                <div className="w-1/2 h-full flex justify-end">
                  {!isPhish && (
                    <div 
                      className="h-full bg-gradient-to-l from-teal-400 to-emerald-600 rounded-l-full"
                      style={{ width: `${percentWidth}%` }}
                    />
                  )}
                </div>
                <div className="w-0.5 h-full bg-slate-700" />
                <div className="w-1/2 h-full flex justify-start">
                  {isPhish && (
                    <div 
                      className="h-full bg-gradient-to-r from-rose-500 to-amber-500 rounded-r-full"
                      style={{ width: `${percentWidth}%` }}
                    />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="text-[11px] text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800 font-mono">
        <span className="text-teal-400">◀ Favors Legitimate</span>
        <span className="text-slate-400">Zero Line</span>
        <span className="text-rose-400">Favors Phishing ▶</span>
      </div>
    </div>
  );
};
