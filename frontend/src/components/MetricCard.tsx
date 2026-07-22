'use client';

import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  subtitle?: string;
}

export default function MetricCard({
  title,
  value,
  icon: Icon,
  change,
  changeType = 'neutral',
  subtitle,
}: MetricCardProps) {
  const changeColors = {
    positive: 'text-emerald-400',
    negative: 'text-red-400',
    neutral: 'text-gray-400',
  };

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-cyan-500/30 transition-all duration-300 group">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-400">{title}</p>
          <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
          {change && (
            <p className={`text-xs font-medium ${changeColors[changeType]}`}>
              {change}
            </p>
          )}
        </div>
        <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center group-hover:bg-cyan-500/20 transition-colors">
          <Icon className="w-5 h-5 text-cyan-400" />
        </div>
      </div>
      {subtitle && (
        <p className="mt-2 text-xs text-gray-500">{subtitle}</p>
      )}
    </div>
  );
}
