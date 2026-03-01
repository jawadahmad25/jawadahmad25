import { useState } from 'react';
import { Zap, ArrowRightLeft, Calculator, Ruler } from 'lucide-react';
import { convertUnit, wavelengthCalculator, scaleGeometry } from '../services/api';

type Tool = 'converter' | 'wavelength' | 'geometry';

export default function QuickActionsPage() {
  const [tool, setTool] = useState<Tool>('converter');

  // Unit converter
  const [convValue, setConvValue] = useState('');
  const [fromUnit, setFromUnit] = useState('dbm');
  const [toUnit, setToUnit] = useState('watts');
  const [convFreq, setConvFreq] = useState('');
  const [convResult, setConvResult] = useState<{ output_value: number; output_unit: string } | null>(null);

  // Wavelength calculator
  const [wlFreq, setWlFreq] = useState('28');
  const [wlResult, setWlResult] = useState<Record<string, number> | null>(null);

  // Geometry scaler
  const [geoParams, setGeoParams] = useState('{"patch_length": 4.5, "patch_width": 3.8, "substrate_height": 0.787}');
  const [geoBaseFreq, setGeoBaseFreq] = useState('2.4');
  const [geoTargetFreq, setGeoTargetFreq] = useState('28');
  const [geoResult, setGeoResult] = useState<Record<string, unknown> | null>(null);

  const UNIT_PAIRS = [
    ['dbm', 'watts'], ['watts', 'dbm'],
    ['ghz', 'wavelength_mm'], ['wavelength_mm', 'ghz'],
    ['db', 'linear'], ['linear', 'db'],
    ['ghz', 'mhz'], ['mhz', 'ghz'],
    ['mm', 'lambda'], ['lambda', 'mm'],
  ];

  const handleConvert = async () => {
    if (!convValue) return;
    try {
      const result = await convertUnit(
        parseFloat(convValue), fromUnit, toUnit,
        convFreq ? parseFloat(convFreq) : undefined,
      );
      setConvResult(result);
    } catch (err) {
      console.error('Conversion failed:', err);
    }
  };

  const handleWavelength = async () => {
    if (!wlFreq) return;
    const result = await wavelengthCalculator(parseFloat(wlFreq));
    setWlResult(result);
  };

  const handleScaleGeometry = async () => {
    try {
      const params = JSON.parse(geoParams);
      const result = await scaleGeometry({
        geometry_params: params,
        base_freq_ghz: parseFloat(geoBaseFreq),
        target_freq_ghz: parseFloat(geoTargetFreq),
      });
      setGeoResult(result);
    } catch (err) {
      console.error('Scaling failed:', err);
    }
  };

  const tools: { id: Tool; label: string; icon: typeof Zap; desc: string }[] = [
    { id: 'converter', label: 'Unit Converter', icon: ArrowRightLeft, desc: 'dBm/W, GHz/mm, dB/linear' },
    { id: 'wavelength', label: 'Wavelength Calculator', icon: Calculator, desc: 'Frequency to wavelength' },
    { id: 'geometry', label: 'Geometry Scaler', icon: Ruler, desc: 'Scale antenna dimensions' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Quick Actions</h1>
        <p className="text-sm text-surface-500 mt-1">Frequently used antenna engineering tools</p>
      </div>

      {/* Tool Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tools.map(t => (
          <button
            key={t.id}
            onClick={() => setTool(t.id)}
            className={`card p-5 text-left transition-all ${
              tool === t.id ? 'border-primary-500 ring-1 ring-primary-500' : 'hover:border-surface-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary-50 dark:bg-primary-900/30 text-primary-600">
                <t.icon size={20} />
              </div>
              <div>
                <p className="font-semibold text-sm text-surface-900 dark:text-white">{t.label}</p>
                <p className="text-xs text-surface-400">{t.desc}</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Unit Converter */}
      {tool === 'converter' && (
        <div className="card p-5 space-y-4">
          <h3 className="font-semibold text-surface-900 dark:text-white">Unit Converter</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div>
              <label className="label">Value</label>
              <input className="input-field" type="number" step="any" value={convValue} onChange={e => setConvValue(e.target.value)} placeholder="Enter value" />
            </div>
            <div>
              <label className="label">From</label>
              <select className="input-field" value={fromUnit} onChange={e => setFromUnit(e.target.value)}>
                {[...new Set(UNIT_PAIRS.map(p => p[0]))].map(u => (
                  <option key={u} value={u}>{u.toUpperCase()}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">To</label>
              <select className="input-field" value={toUnit} onChange={e => setToUnit(e.target.value)}>
                {[...new Set(UNIT_PAIRS.map(p => p[1]))].map(u => (
                  <option key={u} value={u}>{u.toUpperCase()}</option>
                ))}
              </select>
            </div>
            <button onClick={handleConvert} className="btn-primary">Convert</button>
          </div>
          {(fromUnit === 'mm' || fromUnit === 'lambda') && (
            <div className="max-w-xs">
              <label className="label">Frequency (GHz) - required for lambda</label>
              <input className="input-field" type="number" step="any" value={convFreq} onChange={e => setConvFreq(e.target.value)} />
            </div>
          )}
          {convResult && (
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-lg font-bold text-surface-900 dark:text-white">
                {convResult.output_value.toExponential(4)} {convResult.output_unit}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Wavelength Calculator */}
      {tool === 'wavelength' && (
        <div className="card p-5 space-y-4">
          <h3 className="font-semibold text-surface-900 dark:text-white">Wavelength Calculator</h3>
          <div className="flex items-end gap-4">
            <div className="flex-1 max-w-xs">
              <label className="label">Frequency (GHz)</label>
              <input className="input-field" type="number" step="any" value={wlFreq} onChange={e => setWlFreq(e.target.value)} />
            </div>
            <button onClick={handleWavelength} className="btn-primary">Calculate</button>
          </div>
          {wlResult && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {Object.entries(wlResult).map(([key, value]) => (
                <div key={key} className="p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
                  <p className="text-xs text-surface-400">{key.replace(/_/g, ' ')}</p>
                  <p className="text-lg font-bold font-mono text-surface-900 dark:text-white">
                    {typeof value === 'number' ? value.toFixed(4) : value}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Geometry Scaler */}
      {tool === 'geometry' && (
        <div className="card p-5 space-y-4">
          <h3 className="font-semibold text-surface-900 dark:text-white">Geometry Scaler</h3>
          <p className="text-sm text-surface-500">Scale antenna dimensions using f1/f2 = L2/L1 electromagnetic scaling law</p>
          <div>
            <label className="label">Geometry Parameters (JSON)</label>
            <textarea className="input-field font-mono text-xs h-20" value={geoParams} onChange={e => setGeoParams(e.target.value)} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label className="label">Base Frequency (GHz)</label>
              <input className="input-field" type="number" step="any" value={geoBaseFreq} onChange={e => setGeoBaseFreq(e.target.value)} />
            </div>
            <div>
              <label className="label">Target Frequency (GHz)</label>
              <input className="input-field" type="number" step="any" value={geoTargetFreq} onChange={e => setGeoTargetFreq(e.target.value)} />
            </div>
            <button onClick={handleScaleGeometry} className="btn-primary">Scale</button>
          </div>
          {geoResult && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-surface-50 dark:bg-surface-800 rounded-lg">
                <p className="text-xs font-medium text-surface-500 mb-2">Original (mm)</p>
                {Object.entries(geoResult.original as Record<string, number>).map(([k, v]) => (
                  <div key={k} className="flex justify-between text-sm py-0.5">
                    <span className="text-surface-600 dark:text-surface-400">{k}</span>
                    <span className="font-mono">{v.toFixed(4)}</span>
                  </div>
                ))}
              </div>
              <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                <p className="text-xs font-medium text-primary-600 mb-2">Scaled (mm)</p>
                {Object.entries(geoResult.scaled as Record<string, number>).map(([k, v]) => (
                  <div key={k} className="flex justify-between text-sm py-0.5">
                    <span className="text-surface-600 dark:text-surface-400">{k}</span>
                    <span className="font-mono font-bold">{v.toFixed(4)}</span>
                  </div>
                ))}
                <div className="mt-2 pt-2 border-t border-primary-200 dark:border-primary-800">
                  <p className="text-xs text-primary-600">Scaling factor: {(geoResult.scaling_factor as number).toFixed(4)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
