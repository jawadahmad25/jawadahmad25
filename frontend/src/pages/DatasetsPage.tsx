import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Upload, Search, Trash2, Eye, GitCompare, FlaskConical } from 'lucide-react';
import FileUpload from '../components/common/FileUpload';
import DataTable from '../components/common/DataTable';
import { listDatasets, uploadDataset, deleteDataset, previewDataset } from '../services/api';
import type { Dataset } from '../types';

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [previewData, setPreviewData] = useState<{ columns: string[]; data: Record<string, unknown>[] } | null>(null);
  const [previewName, setPreviewName] = useState('');
  const [loading, setLoading] = useState(true);

  // Upload form
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState('');
  const [uploadSource, setUploadSource] = useState('simulation');
  const [uploadBand, setUploadBand] = useState('');
  const [uploadAntennaType, setUploadAntennaType] = useState('');
  const [uploadSubstrate, setUploadSubstrate] = useState('');
  const [uploading, setUploading] = useState(false);

  const loadDatasets = () => {
    setLoading(true);
    listDatasets({ search, limit: 50 })
      .then(res => { setDatasets(res.datasets); setTotal(res.total); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadDatasets(); }, [search]);

  const handleUpload = async () => {
    if (!uploadFile || !uploadName) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('name', uploadName);
    formData.append('source', uploadSource);
    if (uploadBand) formData.append('frequency_band', uploadBand);
    if (uploadAntennaType) formData.append('antenna_type', uploadAntennaType);
    if (uploadSubstrate) formData.append('substrate', uploadSubstrate);

    try {
      await uploadDataset(formData);
      setShowUpload(false);
      setUploadFile(null);
      setUploadName('');
      loadDatasets();
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
    }
  };

  const handlePreview = async (ds: Dataset) => {
    try {
      const data = await previewDataset(ds.id);
      setPreviewData(data);
      setPreviewName(ds.name);
    } catch (err) {
      console.error('Preview failed:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this dataset?')) return;
    await deleteDataset(id);
    loadDatasets();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Datasets</h1>
          <p className="text-sm text-surface-500 mt-1">{total} datasets</p>
        </div>
        <div className="flex gap-2">
          <Link to="/datasets/align" className="btn-secondary flex items-center gap-2">
            <GitCompare size={16} /> Align Data
          </Link>
          <button onClick={() => setShowUpload(!showUpload)} className="btn-primary flex items-center gap-2">
            <Upload size={16} /> Upload Dataset
          </button>
        </div>
      </div>

      {/* Upload Panel */}
      {showUpload && (
        <div className="card p-5 space-y-4">
          <h3 className="font-semibold text-surface-900 dark:text-white">Upload New Dataset</h3>
          <FileUpload onFileSelect={f => { setUploadFile(f); if (!uploadName) setUploadName(f.name.replace(/\.[^.]+$/, '')); }} selectedFile={uploadFile} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Name *</label>
              <input className="input-field" value={uploadName} onChange={e => setUploadName(e.target.value)} placeholder="Dataset name" />
            </div>
            <div>
              <label className="label">Source</label>
              <select className="input-field" value={uploadSource} onChange={e => setUploadSource(e.target.value)}>
                <option value="simulation">Simulation</option>
                <option value="measurement">Measurement</option>
                <option value="synthetic">Synthetic</option>
              </select>
            </div>
            <div>
              <label className="label">Frequency Band</label>
              <input className="input-field" value={uploadBand} onChange={e => setUploadBand(e.target.value)} placeholder="e.g., 28 GHz" />
            </div>
            <div>
              <label className="label">Antenna Type</label>
              <input className="input-field" value={uploadAntennaType} onChange={e => setUploadAntennaType(e.target.value)} placeholder="e.g., Patch Array" />
            </div>
            <div>
              <label className="label">Substrate</label>
              <input className="input-field" value={uploadSubstrate} onChange={e => setUploadSubstrate(e.target.value)} placeholder="e.g., Rogers 5880" />
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={handleUpload} disabled={!uploadFile || !uploadName || uploading} className="btn-primary">
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
            <button onClick={() => setShowUpload(false)} className="btn-secondary">Cancel</button>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={16} />
        <input
          className="input-field pl-9"
          placeholder="Search datasets... (e.g., '28 GHz patch array')"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* Dataset List */}
      <div className="card">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto" />
          </div>
        ) : datasets.length === 0 ? (
          <div className="p-8 text-center text-surface-400">
            <p>No datasets found. Upload your first dataset above.</p>
          </div>
        ) : (
          <div className="divide-y divide-surface-100 dark:divide-surface-800">
            {datasets.map(ds => (
              <div key={ds.id} className="p-4 flex items-center gap-4 hover:bg-surface-50 dark:hover:bg-surface-800/50">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-sm text-surface-900 dark:text-white truncate">{ds.name}</p>
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      ds.source === 'simulation' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                      ds.source === 'measurement' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                      'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
                    }`}>
                      {ds.source}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-surface-400">
                    <span>{ds.file_format}</span>
                    {ds.frequency_band && <span>{ds.frequency_band}</span>}
                    {ds.num_points && <span>{ds.num_points} points</span>}
                    {ds.freq_min != null && ds.freq_max != null && (
                      <span>{ds.freq_min.toFixed(2)}-{ds.freq_max.toFixed(2)} GHz</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => handlePreview(ds)} className="p-2 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg" title="Preview">
                    <Eye size={16} className="text-surface-500" />
                  </button>
                  <button onClick={() => handleDelete(ds.id)} className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg" title="Delete">
                    <Trash2 size={16} className="text-red-500" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Preview Modal */}
      {previewData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setPreviewData(null)}>
          <div className="card max-w-4xl w-full max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <div className="p-4 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between">
              <h3 className="font-semibold">{previewName} - Preview</h3>
              <button onClick={() => setPreviewData(null)} className="text-surface-400 hover:text-surface-600">&times;</button>
            </div>
            <div className="p-4">
              <DataTable columns={previewData.columns} data={previewData.data} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
