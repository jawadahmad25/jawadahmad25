import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Database, Brain, FileText, BarChart3, Plus, ArrowRight } from 'lucide-react';
import StatsCard from '../components/common/StatsCard';
import { getDashboard } from '../services/api';
import type { DashboardStats } from '../types';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  const s = stats?.stats;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
            Antenna ML Research Hub
          </h1>
          <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">
            Your integrated research workflow assistant
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Datasets"
          value={s?.total_datasets ?? 0}
          subtitle="Total uploaded"
          icon={Database}
          color="text-blue-600"
        />
        <StatsCard
          title="Trained Models"
          value={s?.total_models ?? 0}
          subtitle={s?.best_r2 ? `Best R\u00B2: ${s.best_r2.toFixed(4)}` : 'No models yet'}
          icon={Brain}
          color="text-purple-600"
        />
        <StatsCard
          title="Active Papers"
          value={s?.active_papers ?? 0}
          subtitle={`${s?.total_publications ?? 0} total`}
          icon={FileText}
          color="text-green-600"
        />
        <StatsCard
          title="Antenna Designs"
          value={s?.total_designs ?? 0}
          subtitle="In knowledge base"
          icon={BarChart3}
          color="text-orange-600"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/datasets"
          className="card p-5 hover:border-primary-300 dark:hover:border-primary-600 transition-colors group"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600">
              <Plus size={20} />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-surface-900 dark:text-white">New Dataset</h3>
              <p className="text-xs text-surface-500">Upload CST, HFSS, or VNA data</p>
            </div>
            <ArrowRight size={16} className="text-surface-400 group-hover:text-primary-500 transition-colors" />
          </div>
        </Link>

        <Link
          to="/models"
          className="card p-5 hover:border-primary-300 dark:hover:border-primary-600 transition-colors group"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-50 dark:bg-purple-900/30 text-purple-600">
              <Brain size={20} />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-surface-900 dark:text-white">Train Model</h3>
              <p className="text-xs text-surface-500">LR, RF, GB, SVR, Neural Net</p>
            </div>
            <ArrowRight size={16} className="text-surface-400 group-hover:text-primary-500 transition-colors" />
          </div>
        </Link>

        <Link
          to="/datasets/align"
          className="card p-5 hover:border-primary-300 dark:hover:border-primary-600 transition-colors group"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-50 dark:bg-green-900/30 text-green-600">
              <BarChart3 size={20} />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-surface-900 dark:text-white">Align Data</h3>
              <p className="text-xs text-surface-500">Sync simulation & measurement</p>
            </div>
            <ArrowRight size={16} className="text-surface-400 group-hover:text-primary-500 transition-colors" />
          </div>
        </Link>
      </div>

      {/* Recent Datasets */}
      <div className="card">
        <div className="p-5 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between">
          <h2 className="font-semibold text-surface-900 dark:text-white">Recent Datasets</h2>
          <Link to="/datasets" className="text-sm text-primary-600 hover:text-primary-700">
            View all
          </Link>
        </div>
        {stats?.recent_datasets && stats.recent_datasets.length > 0 ? (
          <div className="divide-y divide-surface-100 dark:divide-surface-800">
            {stats.recent_datasets.map(ds => (
              <div key={ds.id} className="p-4 flex items-center justify-between hover:bg-surface-50 dark:hover:bg-surface-800/50">
                <div>
                  <p className="font-medium text-sm text-surface-900 dark:text-white">{ds.name}</p>
                  <p className="text-xs text-surface-400 mt-0.5">
                    {ds.source} {ds.frequency_band ? `| ${ds.frequency_band}` : ''}
                  </p>
                </div>
                <span className="text-xs text-surface-400">
                  {ds.created_at ? new Date(ds.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-surface-400">
            <Database className="mx-auto mb-2" size={24} />
            <p className="text-sm">No datasets yet. Upload your first dataset to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
}
