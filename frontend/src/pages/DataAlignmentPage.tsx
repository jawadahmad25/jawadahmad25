import { useState } from 'react';
import { ArrowLeft, GitCompare, Download } from 'lucide-react';
import { Link } from 'react-router-dom';
import FileUpload from '../components/common/FileUpload';
import DataTable from '../components/common/DataTable';
import { alignDatasets } from '../services/api';
import type { AlignmentResponse } from '../types';

export default function DataAlignmentPage() {
  const [refFile, setRefFile] = useState<File | null>(null);
  const [targetFile, setTargetFile] = useState<File | null>(null);
  const [method, setMethod] = useState('cubic');
  const [result, setResult] = useState<AlignmentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAlign = async () => {
    if (!refFile || !targetFile) return;
    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('reference_file', refFile);
    formData.append('target_file', targetFile);
    formData.append('interpolation_method', method);

    try {
      const res = await alignDatasets(formData);
      setResult(res);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Alignment failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/datasets" className="p-2 hover:bg-surface-100 dark:hover:bg-surface-800 rounded-lg">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Data Alignment Tool</h1>
          <p className="text-sm text-surface-500 mt-1">
            Align measured vs simulated data onto a common frequency grid
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Reference File */}
        <div className="card p-5">
          <h3 className="font-semibold mb-3 text-surface-900 dark:text-white">
            Reference File (Simulation)
          </h3>
          <p className="text-xs text-surface-400 mb-3">
            This defines the frequency grid. Target will be interpolated onto this grid.
          </p>
          <FileUpload
            onFileSelect={setRefFile}
            selectedFile={refFile}
            label="Upload simulation data"
          />
          {refFile && (
            <p className="text-xs text-green-600 mt-2">Selected: {refFile.name}</p>
          )}
        </div>

        {/* Target File */}
        <div className="card p-5">
          <h3 className="font-semibold mb-3 text-surface-900 dark:text-white">
            Target File (Measurement)
          </h3>
          <p className="text-xs text-surface-400 mb-3">
            This data will be interpolated to match the reference frequency grid.
          </p>
          <FileUpload
            onFileSelect={setTargetFile}
            selectedFile={targetFile}
            label="Upload measurement data"
          />
          {targetFile && (
            <p className="text-xs text-green-600 mt-2">Selected: {targetFile.name}</p>
          )}
        </div>
      </div>

      {/* Options */}
      <div className="card p-5">
        <div className="flex items-end gap-4">
          <div className="flex-1 max-w-xs">
            <label className="label">Interpolation Method</label>
            <select className="input-field" value={method} onChange={e => setMethod(e.target.value)}>
              <option value="linear">Linear</option>
              <option value="cubic">Cubic (Recommended)</option>
              <option value="quadratic">Quadratic</option>
            </select>
          </div>
          <button
            onClick={handleAlign}
            disabled={!refFile || !targetFile || loading}
            className="btn-primary flex items-center gap-2"
          >
            <GitCompare size={16} />
            {loading ? 'Aligning...' : 'Align Data'}
          </button>
        </div>
      </div>

      {error && (
        <div className="card p-4 border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <div className="card p-5">
            <h3 className="font-semibold mb-4 text-surface-900 dark:text-white">Alignment Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">Reference</p>
                <p className="text-lg font-bold text-surface-900 dark:text-white">{result.reference_points} points</p>
              </div>
              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-xs text-green-600 dark:text-green-400 font-medium">Target (Original)</p>
                <p className="text-lg font-bold text-surface-900 dark:text-white">{result.target_points_original} points</p>
              </div>
              <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-xs text-purple-600 dark:text-purple-400 font-medium">Aligned Output</p>
                <p className="text-lg font-bold text-surface-900 dark:text-white">{result.target_points_aligned} points</p>
              </div>
            </div>
            <div className="mt-3 text-sm text-surface-500">
              Frequency range: {result.freq_min.toFixed(4)} - {result.freq_max.toFixed(4)} GHz
              (step: {result.freq_step.toFixed(4)} GHz)
            </div>
            <div className="mt-4">
              <a
                href={`/api/datasets/download?path=${encodeURIComponent(result.aligned_file_path)}`}
                className="btn-primary inline-flex items-center gap-2"
                download
              >
                <Download size={16} /> Download Aligned CSV
              </a>
            </div>
          </div>

          {/* Preview */}
          {result.preview_data && (
            <div className="card p-5">
              <h3 className="font-semibold mb-3 text-surface-900 dark:text-white">
                Data Preview ({result.preview_data.preview_rows} of {result.preview_data.total_rows} rows)
              </h3>
              <DataTable
                columns={result.preview_data.columns}
                data={result.preview_data.data}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
