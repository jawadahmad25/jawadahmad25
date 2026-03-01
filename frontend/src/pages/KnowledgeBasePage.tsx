import { useState, useEffect } from 'react';
import { BookOpen, Plus, Search, Eye } from 'lucide-react';
import { listDesigns, createDesign, getInsights } from '../services/api';
import type { AntennaDesign } from '../types';

export default function KnowledgeBasePage() {
  const [designs, setDesigns] = useState<AntennaDesign[]>([]);
  const [insights, setInsights] = useState<Record<string, unknown> | null>(null);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [tab, setTab] = useState<'designs' | 'insights'>('designs');

  // Form
  const [designName, setDesignName] = useState('');
  const [freqBand, setFreqBand] = useState('');
  const [antennaType, setAntennaType] = useState('');
  const [substrate, setSubstrate] = useState('');
  const [application, setApplication] = useState('');
  const [peakGain, setPeakGain] = useState('');
  const [bandwidth, setBandwidth] = useState('');
  const [s11Min, setS11Min] = useState('');

  useEffect(() => {
    loadDesigns();
    getInsights().then(setInsights).catch(console.error);
  }, []);

  const loadDesigns = () => {
    listDesigns({ search, limit: 100 })
      .then(setDesigns)
      .catch(console.error);
  };

  useEffect(() => { loadDesigns(); }, [search]);

  const handleAdd = async () => {
    if (!designName) return;
    await createDesign({
      name: designName,
      frequency_band: freqBand || undefined,
      antenna_type: antennaType || undefined,
      substrate: substrate || undefined,
      application: application || undefined,
      peak_gain_dbi: peakGain ? parseFloat(peakGain) : undefined,
      bandwidth_mhz: bandwidth ? parseFloat(bandwidth) : undefined,
      s11_min_db: s11Min ? parseFloat(s11Min) : undefined,
    });
    setShowAdd(false);
    setDesignName('');
    loadDesigns();
  };

  const summary = (insights as Record<string, Record<string, unknown>>)?.summary as Record<string, unknown> | undefined;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Knowledge Base</h1>
          <p className="text-sm text-surface-500 mt-1">Antenna design library and research insights</p>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Add Design
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-100 dark:bg-surface-800 p-1 rounded-lg w-fit">
        <button onClick={() => setTab('designs')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === 'designs' ? 'bg-white dark:bg-surface-700 text-surface-900 dark:text-white shadow-sm' : 'text-surface-500'}`}>
          Designs
        </button>
        <button onClick={() => setTab('insights')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === 'insights' ? 'bg-white dark:bg-surface-700 text-surface-900 dark:text-white shadow-sm' : 'text-surface-500'}`}>
          Insights
        </button>
      </div>

      {tab === 'designs' && (
        <>
          {/* Add Design Panel */}
          {showAdd && (
            <div className="card p-5 space-y-4">
              <h3 className="font-semibold text-surface-900 dark:text-white">New Antenna Design</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="label">Name *</label>
                  <input className="input-field" value={designName} onChange={e => setDesignName(e.target.value)} placeholder="e.g., 4x4 Butler Matrix" />
                </div>
                <div>
                  <label className="label">Frequency Band</label>
                  <input className="input-field" value={freqBand} onChange={e => setFreqBand(e.target.value)} placeholder="e.g., 28 GHz" />
                </div>
                <div>
                  <label className="label">Antenna Type</label>
                  <input className="input-field" value={antennaType} onChange={e => setAntennaType(e.target.value)} placeholder="e.g., Patch Array" />
                </div>
                <div>
                  <label className="label">Substrate</label>
                  <input className="input-field" value={substrate} onChange={e => setSubstrate(e.target.value)} placeholder="e.g., Rogers 5880" />
                </div>
                <div>
                  <label className="label">Application</label>
                  <input className="input-field" value={application} onChange={e => setApplication(e.target.value)} placeholder="e.g., V2V, 5G" />
                </div>
                <div>
                  <label className="label">Peak Gain (dBi)</label>
                  <input className="input-field" type="number" step="0.1" value={peakGain} onChange={e => setPeakGain(e.target.value)} />
                </div>
                <div>
                  <label className="label">Bandwidth (MHz)</label>
                  <input className="input-field" type="number" value={bandwidth} onChange={e => setBandwidth(e.target.value)} />
                </div>
                <div>
                  <label className="label">S11 Min (dB)</label>
                  <input className="input-field" type="number" step="0.1" value={s11Min} onChange={e => setS11Min(e.target.value)} />
                </div>
              </div>
              <button onClick={handleAdd} className="btn-primary">Add Design</button>
            </div>
          )}

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={16} />
            <input className="input-field pl-9" placeholder="Search designs... (e.g., '28 GHz patch array Rogers 5880')" value={search} onChange={e => setSearch(e.target.value)} />
          </div>

          {/* Design List */}
          <div className="card">
            {designs.length === 0 ? (
              <div className="p-8 text-center text-surface-400">
                <BookOpen className="mx-auto mb-2" size={24} />
                <p className="text-sm">No designs in library yet.</p>
              </div>
            ) : (
              <div className="divide-y divide-surface-100 dark:divide-surface-800">
                {designs.map(d => (
                  <div key={d.id} className="p-4 hover:bg-surface-50 dark:hover:bg-surface-800/50">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-surface-900 dark:text-white">{d.name}</p>
                        <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-surface-400">
                          {d.frequency_band && <span className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded-full">{d.frequency_band}</span>}
                          {d.antenna_type && <span className="px-2 py-0.5 bg-green-50 dark:bg-green-900/20 text-green-600 rounded-full">{d.antenna_type}</span>}
                          {d.substrate && <span className="px-2 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 rounded-full">{d.substrate}</span>}
                          {d.application && <span>{d.application}</span>}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-xs text-surface-500">
                          {d.peak_gain_dbi != null && <span>Gain: {d.peak_gain_dbi} dBi</span>}
                          {d.bandwidth_mhz != null && <span>BW: {d.bandwidth_mhz} MHz</span>}
                          {d.s11_min_db != null && <span>S11: {d.s11_min_db} dB</span>}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {tab === 'insights' && insights && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-surface-900 dark:text-white">{summary?.total_datasets as number ?? 0}</p>
              <p className="text-xs text-surface-400">Datasets</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-surface-900 dark:text-white">{summary?.total_models as number ?? 0}</p>
              <p className="text-xs text-surface-400">Models</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-surface-900 dark:text-white">{summary?.total_designs as number ?? 0}</p>
              <p className="text-xs text-surface-400">Designs</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-primary-600">
                {(summary?.best_r2 as number | null) != null ? (summary?.best_r2 as number).toFixed(4) : 'N/A'}
              </p>
              <p className="text-xs text-surface-400">Best R2</p>
            </div>
          </div>

          {(insights as Record<string, unknown>).best_models && (
            <div className="card p-5">
              <h3 className="font-semibold mb-3 text-surface-900 dark:text-white">Top Models</h3>
              <div className="space-y-2">
                {((insights as Record<string, unknown>).best_models as Record<string, unknown>[]).map((m: Record<string, unknown>, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-surface-50 dark:bg-surface-800 rounded-lg">
                    <span className="text-sm">{m.name as string}</span>
                    <span className="text-sm font-mono font-bold text-green-600">R2: {(m.r2 as number).toFixed(4)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
