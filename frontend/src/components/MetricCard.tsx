import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'cyan' | 'teal' | 'rose' | 'amber' | 'slate';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  icon: Icon,
  variant = 'cyan'
}) => {
  const variantStyles = {
    cyan: {
      border: 'border-slate-800 hover:border-cyan-500/50',
      iconBg: 'bg-cyan-950/60 text-cyan-400 border border-cyan-800/60',
      text: 'text-cyan-400',
    },
    teal: {
      border: 'border-slate-800 hover:border-teal-500/50',
      iconBg: 'bg-teal-950/60 text-teal-400 border border-teal-800/60',
      text: 'text-teal-400',
    },
    rose: {
      border: 'border-slate-800 hover:border-rose-500/50',
      iconBg: 'bg-rose-950/60 text-rose-400 border border-rose-800/60',
      text: 'text-rose-400',
    },
    amber: {
      border: 'border-slate-800 hover:border-amber-500/50',
      iconBg: 'bg-amber-950/60 text-amber-400 border border-amber-800/60',
      text: 'text-amber-400',
    },
    slate: {
      border: 'border-slate-800 hover:border-slate-700',
      iconBg: 'bg-slate-800 text-slate-300 border border-slate-700',
      text: 'text-slate-100',
    },
  }[variant];

  return (
    <div className={`p-5 rounded-xl bg-slate-900/70 border ${variantStyles.border} transition-all duration-200 backdrop-blur-sm group`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110 ${variantStyles.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="text-2xl font-bold font-mono tracking-tight text-white mb-1">
        {value}
      </div>
      {subtitle && (
        <p className="text-xs text-slate-400 leading-relaxed font-sans">{subtitle}</p>
      )}
    </div>
  );
};
