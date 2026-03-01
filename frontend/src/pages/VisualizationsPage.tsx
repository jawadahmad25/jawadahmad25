import { useState, useEffect } from 'react';
import { BarChart3, Download } from 'lucide-react';
import { listDatasets, generateFigure } from '../services/api';
import type { Dataset } from '../types';

const PLOT_TYPES = [
  { id: 's_parameter', label: 'S-Parameter Plot', desc: 'S11, S21 vs Frequency' },
  { id: 'radiation_pattern', label: 'Radiation Pattern', desc: 'Polar gain pattern' },
  { id: 'gain_vs_angle', label: 'Gain vs Angle', desc: 'Cartesian gain plot' },
  { id: 'ml_comparison', label: 'Model Comparison', desc: 'Bar chart of ML metrics' },
  { id: 'actual_vs_predicted', label: 'Actual vs Predicted', desc: 'Scatter with ideal line' },
  { id: 'rssi_distance', label: 'RSSI vs Distance', desc: 'V2V signal strength' },
  { id: 'scatter', label: 'Scatter Plot', desc: 'Generic X-Y scatter' },
];

const EXPORT_FORMATS = ['png', 'pdf', 'eps', 'svg'];

export default function VisualizationsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [plotType, setPlotType] = useState('s_parameter');
  const [datasetId, setDatasetId] = useState<number>(0);
  const [title, setTitle] = useState('');
  const [xLabel, setXLabel] = useState('Frequency (GHz)');
  const [yLabel, setYLabel] = useState('|S11| (dB)');
  const [exportFormat, setExportFormat] = useState('png');
  const [dpi, setDpi] = useState(600);
  const [width, setWidth] = useState(3.5);
  const [height, setHeight] = useState(2.625);
  const [preview, setPreview] = useState<string | null>(null);
  const [filePath, setFilePath] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listDatasets({ limit: 100 }).then(r => setDatasets(r.datasets)).catch(console.error);
  }, []);

  const handleGenerate = async () => {
    setLoading(true);
    setPreview(null);
    try {
      const result = await generateFigure({
        plot_type: plotType,
        dataset_id: datasetId || undefined,
        title: title || undefined,
        x_label: xLabel,
        y_label: yLabel,
        export_format: exportFormat,
        dpi,
        width_inches: width,
        height_inches: height,
      });
      setPreview(result.preview_base64);
      setFilePath(result.file_path);
    } catch (err) {
      console.error('Figure generation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Visualizations</h1>
        <p className="text-sm text-surface-500 mt-1">Generate publication-quality figures (IEEE/Elsevier)</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Config Panel */}
        <div className="lg:col-span-1 space-y-4">
          <div className="card p-5 space-y-4">
            <h3 className="font-semibold text-surface-900 dark:text-white">Plot Configuration</h3>

            <div>
              <label className="label">Plot Type</label>
              <select className="input-field" value={plotType} onChange={e => setPlotType(e.target.value)}>
                {PLOT_TYPES.map(pt => (
                  <option key={pt.id} value={pt.id}>{pt.label}</option>
                ))}
              </select>
              <p className="text-xs text-surface-400 mt-1">
                {PLOT_TYPES.find(p => p.id === plotType)?.desc}
              </p>
            </div>

            <div>
              <label className="label">Dataset</label>
              <select className="input-field" value={datasetId} onChange={e => setDatasetId(Number(e.target.value))}>
                <option value={0}>Select dataset...</option>
                {datasets.map(ds => (
                  <option key={ds.id} value={ds.id}>{ds.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">Title</label>
              <input className="input-field" value={title} onChange={e => setTitle(e.target.value)} placeholder="Figure title" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">X Label</label>
                <input className="input-field" value={xLabel} onChange={e => setXLabel(e.target.value)} />
              </div>
              <div>
                <label className="label">Y Label</label>
                <input className="input-field" value={yLabel} onChange={e => setYLabel(e.target.value)} />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="label">Width (in)</label>
                <input className="input-field" type="number" step="0.25" value={width} onChange={e => setWidth(Number(e.target.value))} />
              </div>
              <div>
                <label className="label">Height (in)</label>
                <input className="input-field" type="number" step="0.25" value={height} onChange={e => setHeight(Number(e.target.value))} />
              </div>
              <div>
                <label className="label">DPI</label>
                <input className="input-field" type="number" step="100" value={dpi} onChange={e => setDpi(Number(e.target.value))} />
              </div>
            </div>

            <div>
              <label className="label">Export Format</label>
              <select className="input-field" value={exportFormat} onChange={e => setExportFormat(e.target.value)}>
                {EXPORT_FORMATS.map(fmt => (
                  <option key={fmt} value={fmt}>{fmt.toUpperCase()}</option>
                ))}
              </select>
            </div>

            <button onClick={handleGenerate} disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              <BarChart3 size={16} />
              {loading ? 'Generating...' : 'Generate Figure'}
            </button>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="lg:col-span-2">
          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-surface-900 dark:text-white">Preview</h3>
              {filePath && (
                <button className="btn-secondary flex items-center gap-2 text-xs">
                  <Download size={14} /> Download
                </button>
              )}
            </div>
            {preview ? (
              <img
                src={`data:image/png;base64,${preview}`}
                alt="Generated figure"
                className="max-w-full mx-auto border border-surface-200 dark:border-surface-700 rounded-lg"
              />
            ) : (
              <div className="flex items-center justify-center h-64 bg-surface-50 dark:bg-surface-800 rounded-lg">
                <div className="text-center text-surface-400">
                  <BarChart3 className="mx-auto mb-2" size={32} />
                  <p className="text-sm">Select a dataset and click Generate to create a figure</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
