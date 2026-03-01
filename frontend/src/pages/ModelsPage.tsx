import { useState, useEffect } from 'react';
import { Brain, Play, Search, Trash2, TrendingUp } from 'lucide-react';
import { listModels, listDatasets, trainModels, deleteModel, predictModel } from '../services/api';
import type { MLModel, Dataset, TrainingResponse, ModelResult } from '../types';

const MODEL_TYPES = [
  { id: 'linear_regression', label: 'Linear Regression' },
  { id: 'random_forest', label: 'Random Forest' },
  { id: 'gradient_boosting', label: 'Gradient Boosting' },
  { id: 'svr', label: 'SVR' },
  { id: 'neural_network', label: 'Neural Network' },
];

export default function ModelsPage() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [showTrain, setShowTrain] = useState(false);
  const [showPredict, setShowPredict] = useState(false);
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
  const [trainingResult, setTrainingResult] = useState<TrainingResponse | null>(null);
  const [search, setSearch] = useState('');

  // Training form
  const [trainDatasetId, setTrainDatasetId] = useState<number>(0);
  const [trainTarget, setTrainTarget] = useState('');
  const [trainFeatures, setTrainFeatures] = useState<string[]>([]);
  const [trainModelTypes, setTrainModelTypes] = useState<string[]>(['random_forest', 'gradient_boosting']);
  const [availableColumns, setAvailableColumns] = useState<string[]>([]);
  const [training, setTraining] = useState(false);

  // Prediction form
  const [predictInputs, setPredictInputs] = useState<Record<string, string>>({});
  const [prediction, setPrediction] = useState<number | null>(null);

  useEffect(() => {
    loadModels();
    listDatasets({ limit: 100 }).then(r => setDatasets(r.datasets)).catch(console.error);
  }, []);

  const loadModels = () => {
    listModels({ search, limit: 100 })
      .then(r => setModels(r.models))
      .catch(console.error);
  };

  useEffect(() => { loadModels(); }, [search]);

  const handleDatasetChange = (dsId: number) => {
    setTrainDatasetId(dsId);
    const ds = datasets.find(d => d.id === dsId);
    if (ds?.columns) {
      setAvailableColumns(ds.columns);
      setTrainTarget('');
      setTrainFeatures([]);
    }
  };

  const handleTrain = async () => {
    if (!trainDatasetId || !trainTarget || trainFeatures.length === 0) return;
    setTraining(true);
    setTrainingResult(null);
    try {
      const result = await trainModels({
        dataset_id: trainDatasetId,
        target_variable: trainTarget,
        feature_columns: trainFeatures,
        model_types: trainModelTypes,
        test_size: 0.2,
      });
      setTrainingResult(result);
      loadModels();
    } catch (err) {
      console.error('Training failed:', err);
    } finally {
      setTraining(false);
    }
  };

  const handlePredict = async () => {
    if (!selectedModel) return;
    const features: Record<string, number> = {};
    for (const [key, val] of Object.entries(predictInputs)) {
      features[key] = parseFloat(val) || 0;
    }
    try {
      const result = await predictModel({ model_id: selectedModel.id, input_features: features });
      setPrediction(result.prediction);
    } catch (err) {
      console.error('Prediction failed:', err);
    }
  };

  const openPredict = (model: MLModel) => {
    setSelectedModel(model);
    const inputs: Record<string, string> = {};
    for (const col of model.feature_columns) {
      inputs[col] = '';
    }
    setPredictInputs(inputs);
    setPrediction(null);
    setShowPredict(true);
  };

  const formatModelType = (t: string) =>
    t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">ML Models</h1>
          <p className="text-sm text-surface-500 mt-1">{models.length} trained models</p>
        </div>
        <button onClick={() => setShowTrain(!showTrain)} className="btn-primary flex items-center gap-2">
          <Play size={16} /> Train Models
        </button>
      </div>

      {/* Training Panel */}
      {showTrain && (
        <div className="card p-5 space-y-4">
          <h3 className="font-semibold text-surface-900 dark:text-white">Train New Models</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Dataset</label>
              <select className="input-field" value={trainDatasetId} onChange={e => handleDatasetChange(Number(e.target.value))}>
                <option value={0}>Select dataset...</option>
                {datasets.map(ds => (
                  <option key={ds.id} value={ds.id}>{ds.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">Target Variable</label>
              <select className="input-field" value={trainTarget} onChange={e => setTrainTarget(e.target.value)}>
                <option value="">Select target...</option>
                {availableColumns.map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>
          </div>

          {availableColumns.length > 0 && (
            <div>
              <label className="label">Feature Columns</label>
              <div className="flex flex-wrap gap-2">
                {availableColumns.filter(c => c !== trainTarget).map(col => (
                  <label key={col} className="flex items-center gap-1.5 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={trainFeatures.includes(col)}
                      onChange={e => {
                        if (e.target.checked) setTrainFeatures([...trainFeatures, col]);
                        else setTrainFeatures(trainFeatures.filter(f => f !== col));
                      }}
                      className="rounded text-primary-600"
                    />
                    <span className="text-surface-700 dark:text-surface-300">{col}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div>
            <label className="label">Models to Train</label>
            <div className="flex flex-wrap gap-2">
              {MODEL_TYPES.map(mt => (
                <label key={mt.id} className="flex items-center gap-1.5 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={trainModelTypes.includes(mt.id)}
                    onChange={e => {
                      if (e.target.checked) setTrainModelTypes([...trainModelTypes, mt.id]);
                      else setTrainModelTypes(trainModelTypes.filter(t => t !== mt.id));
                    }}
                    className="rounded text-primary-600"
                  />
                  <span className="text-surface-700 dark:text-surface-300">{mt.label}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={handleTrain}
            disabled={!trainDatasetId || !trainTarget || trainFeatures.length === 0 || training}
            className="btn-primary flex items-center gap-2"
          >
            <Brain size={16} />
            {training ? 'Training...' : 'Train All Models'}
          </button>
        </div>
      )}

      {/* Training Results */}
      {trainingResult && (
        <div className="card p-5">
          <h3 className="font-semibold mb-4 text-surface-900 dark:text-white">
            Training Results - {trainingResult.dataset_name}
          </h3>
          <p className="text-sm text-surface-500 mb-4">
            Target: {trainingResult.target_variable} | Train: {trainingResult.num_training_samples} | Test: {trainingResult.num_test_samples}
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-200 dark:border-surface-700">
                  <th className="text-left py-2 px-3 font-medium">Model</th>
                  <th className="text-right py-2 px-3 font-medium">MSE</th>
                  <th className="text-right py-2 px-3 font-medium">RMSE</th>
                  <th className="text-right py-2 px-3 font-medium">MAE</th>
                  <th className="text-right py-2 px-3 font-medium">R2</th>
                  <th className="text-right py-2 px-3 font-medium">Time (s)</th>
                </tr>
              </thead>
              <tbody>
                {trainingResult.results
                  .sort((a, b) => b.r2_score - a.r2_score)
                  .map((r: ModelResult) => (
                  <tr key={r.model_type} className="border-b border-surface-100 dark:border-surface-800">
                    <td className="py-2 px-3 font-medium">{formatModelType(r.model_type)}</td>
                    <td className="py-2 px-3 text-right font-mono text-xs">{r.mse.toFixed(6)}</td>
                    <td className="py-2 px-3 text-right font-mono text-xs">{r.rmse.toFixed(6)}</td>
                    <td className="py-2 px-3 text-right font-mono text-xs">{r.mae.toFixed(6)}</td>
                    <td className="py-2 px-3 text-right font-mono text-xs font-bold">
                      <span className={r.r2_score > 0.9 ? 'text-green-600' : r.r2_score > 0.7 ? 'text-yellow-600' : 'text-red-600'}>
                        {r.r2_score.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right font-mono text-xs">{r.training_duration_seconds.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={16} />
        <input className="input-field pl-9" placeholder="Search models..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {/* Model List */}
      <div className="card">
        {models.length === 0 ? (
          <div className="p-8 text-center text-surface-400">
            <Brain className="mx-auto mb-2" size={24} />
            <p className="text-sm">No models trained yet. Select a dataset and train your first model.</p>
          </div>
        ) : (
          <div className="divide-y divide-surface-100 dark:divide-surface-800">
            {models.map(m => (
              <div key={m.id} className="p-4 flex items-center gap-4 hover:bg-surface-50 dark:hover:bg-surface-800/50">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-sm text-surface-900 dark:text-white">{m.name}</p>
                    <span className="px-2 py-0.5 text-xs bg-surface-100 dark:bg-surface-700 rounded-full">
                      {formatModelType(m.model_type)}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-surface-400">
                    <span>Target: {m.target_variable}</span>
                    {m.r2_score != null && (
                      <span className={m.r2_score > 0.9 ? 'text-green-600 font-medium' : ''}>
                        R2: {m.r2_score.toFixed(4)}
                      </span>
                    )}
                    {m.rmse != null && <span>RMSE: {m.rmse.toFixed(4)}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => openPredict(m)} className="p-2 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg" title="Predict">
                    <TrendingUp size={16} className="text-primary-500" />
                  </button>
                  <button onClick={() => { deleteModel(m.id); loadModels(); }} className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg" title="Delete">
                    <Trash2 size={16} className="text-red-500" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Prediction Modal */}
      {showPredict && selectedModel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowPredict(false)}>
          <div className="card max-w-md w-full" onClick={e => e.stopPropagation()}>
            <div className="p-4 border-b border-surface-200 dark:border-surface-700">
              <h3 className="font-semibold">Predict with {selectedModel.name}</h3>
            </div>
            <div className="p-4 space-y-3">
              {selectedModel.feature_columns.map(col => (
                <div key={col}>
                  <label className="label">{col}</label>
                  <input
                    className="input-field"
                    type="number"
                    step="any"
                    value={predictInputs[col] || ''}
                    onChange={e => setPredictInputs({ ...predictInputs, [col]: e.target.value })}
                    placeholder={`Enter ${col}`}
                  />
                </div>
              ))}
              <button onClick={handlePredict} className="btn-primary w-full">Predict</button>
              {prediction !== null && (
                <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg text-center">
                  <p className="text-sm text-green-600 dark:text-green-400">Prediction</p>
                  <p className="text-2xl font-bold text-surface-900 dark:text-white">{prediction.toFixed(4)}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
