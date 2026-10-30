import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Info } from 'lucide-react';

interface RiskBadgeProps {
  prediction?: string;
  severity?: 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  riskLevel?: 'High' | 'Medium' | 'Low';
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  prediction,
  severity,
  riskLevel,
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5 font-semibold'
  }[size];

  if (prediction) {
    const isPhish = prediction.toLowerCase().includes('phishing');
    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-full font-mono border ${
          isPhish
            ? 'bg-rose-950/70 border-rose-800 text-rose-300'
            : 'bg-emerald-950/70 border-emerald-800 text-emerald-300'
        } ${sizeClasses}`}
      >
        {isPhish ? (
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
        ) : (
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        )}
        {prediction}
      </span>
    );
  }

  const level = severity || riskLevel?.toUpperCase() || 'INFO';

  const styles = {
    HIGH: {
      bg: 'bg-rose-950/70 border-rose-800 text-rose-300',
      icon: ShieldAlert,
      iconColor: 'text-rose-400',
    },
    MEDIUM: {
      bg: 'bg-amber-950/70 border-amber-800 text-amber-300',
      icon: AlertTriangle,
      iconColor: 'text-amber-400',
    },
    LOW: {
      bg: 'bg-slate-800/80 border-slate-700 text-slate-300',
      icon: Info,
      iconColor: 'text-slate-400',
    },
    INFO: {
      bg: 'bg-cyan-950/60 border-cyan-800 text-cyan-300',
      icon: Info,
      iconColor: 'text-cyan-400',
    },
  }[level] || {
    bg: 'bg-slate-800 border-slate-700 text-slate-300',
    icon: Info,
    iconColor: 'text-slate-400',
  };

  const Icon = styles.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-mono border ${styles.bg} ${sizeClasses}`}>
      <Icon className={`w-3.5 h-3.5 ${styles.iconColor}`} />
      {level}
    </span>
  );
};
