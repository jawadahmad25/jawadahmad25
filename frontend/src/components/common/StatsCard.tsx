import { type LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: string;
}

export default function StatsCard({ title, value, subtitle, icon: Icon, color = 'text-primary-600' }: StatsCardProps) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-surface-500 dark:text-surface-400">{title}</p>
          <p className="text-2xl font-bold mt-1 text-surface-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="text-xs text-surface-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-2.5 rounded-lg bg-surface-100 dark:bg-surface-700 ${color}`}>
          <Icon size={20} />
        </div>
      </div>
    </div>
  );
}
