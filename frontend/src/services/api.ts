import axios from 'axios';
import type {
  DatasetListResponse,
  Dataset,
  AlignmentResponse,
  TrainingRequest,
  TrainingResponse,
  MLModel,
  PredictionResponse,
  Publication,
  LatexTableResponse,
  HighlightsResponse,
  AntennaDesign,
  DashboardStats,
  UnitConversion,
  FigureRequest,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// ── Dashboard ──

export const getDashboard = () =>
  api.get<DashboardStats>('/dashboard').then(r => r.data);

// ── Datasets ──

export const listDatasets = (params?: Record<string, string | number>) =>
  api.get<DatasetListResponse>('/datasets/', { params }).then(r => r.data);

export const getDataset = (id: number) =>
  api.get<Dataset>(`/datasets/${id}`).then(r => r.data);

export const uploadDataset = (formData: FormData) =>
  api.post<Dataset>('/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);

export const updateDataset = (id: number, data: Partial<Dataset>) =>
  api.put<Dataset>(`/datasets/${id}`, data).then(r => r.data);

export const deleteDataset = (id: number) =>
  api.delete(`/datasets/${id}`).then(r => r.data);

export const previewDataset = (id: number, rows = 50) =>
  api.get(`/datasets/${id}/preview`, { params: { rows } }).then(r => r.data);

export const alignDatasets = (formData: FormData) =>
  api.post<AlignmentResponse>('/datasets/align', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);

export const generateSyntheticData = (data: {
  base_dataset_id: number;
  base_frequency_ghz: number;
  target_frequency_ghz: number;
  scaling_method?: string;
  output_name?: string;
}) => api.post('/datasets/synthetic', data).then(r => r.data);

// ── ML Models ──

export const trainModels = (data: TrainingRequest) =>
  api.post<TrainingResponse>('/models/train', data).then(r => r.data);

export const listModels = (params?: Record<string, string | number>) =>
  api.get<{ models: MLModel[]; total: number }>('/models/', { params }).then(r => r.data);

export const getModel = (id: number) =>
  api.get<MLModel>(`/models/${id}`).then(r => r.data);

export const predictModel = (data: { model_id: number; input_features: Record<string, number> }) =>
  api.post<PredictionResponse>('/models/predict', data).then(r => r.data);

export const deleteModel = (id: number) =>
  api.delete(`/models/${id}`).then(r => r.data);

// ── Visualizations ──

export const generateFigure = (data: FigureRequest) =>
  api.post('/visualizations/generate', data).then(r => r.data);

export const generateInteractiveFigure = (data: FigureRequest) =>
  api.post('/visualizations/generate/interactive', data).then(r => r.data);

// ── Publications ──

export const createPublication = (data: Partial<Publication>) =>
  api.post<Publication>('/publications/', data).then(r => r.data);

export const listPublications = (params?: Record<string, string>) =>
  api.get<Publication[]>('/publications/', { params }).then(r => r.data);

export const generateLatexTable = (data: {
  data?: Record<string, unknown>[];
  csv_text?: string;
  caption?: string;
  label?: string;
  font_size?: string;
  orientation?: string;
  bold_header?: boolean;
}) => api.post<LatexTableResponse>('/publications/latex-table', data).then(r => r.data);

export const generateHighlights = (data: {
  abstract: string;
  num_highlights?: number;
  max_chars?: number;
}) => api.post<HighlightsResponse>('/publications/highlights', data).then(r => r.data);

export const addCitation = (data: { bibtex: string; publication_id?: number; tags?: string[] }) =>
  api.post('/publications/citations', data).then(r => r.data);

export const listCitations = (params?: Record<string, string | number>) =>
  api.get('/publications/citations/', { params }).then(r => r.data);

// ── Knowledge Base ──

export const createDesign = (data: Partial<AntennaDesign>) =>
  api.post<AntennaDesign>('/knowledge-base/designs', data).then(r => r.data);

export const listDesigns = (params?: Record<string, string | number>) =>
  api.get<AntennaDesign[]>('/knowledge-base/designs', { params }).then(r => r.data);

export const getDesign = (id: number) =>
  api.get<AntennaDesign>(`/knowledge-base/designs/${id}`).then(r => r.data);

export const getCrossReferences = (resourceType: string, resourceId: number) =>
  api.get(`/knowledge-base/cross-reference/${resourceType}/${resourceId}`).then(r => r.data);

export const getInsights = () =>
  api.get('/knowledge-base/insights').then(r => r.data);

// ── Quick Actions ──

export const convertUnit = (value: number, fromUnit: string, toUnit: string, freqGhz?: number) =>
  api.post<UnitConversion>('/quick-actions/convert-unit', null, {
    params: { value, from_unit: fromUnit, to_unit: toUnit, freq_ghz: freqGhz },
  }).then(r => r.data);

export const scaleGeometry = (data: {
  geometry_params: Record<string, number>;
  base_freq_ghz: number;
  target_freq_ghz: number;
}) => api.post('/quick-actions/scale-geometry', data).then(r => r.data);

export const wavelengthCalculator = (freqGhz: number) =>
  api.get('/quick-actions/wavelength-calculator', { params: { freq_ghz: freqGhz } }).then(r => r.data);

export default api;
