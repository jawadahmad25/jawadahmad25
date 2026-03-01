// Dataset types
export interface Dataset {
  id: number;
  name: string;
  description: string | null;
  file_path: string;
  original_filename: string;
  file_format: string;
  frequency_band: string | null;
  antenna_type: string | null;
  source: string;
  substrate: string | null;
  freq_min: number | null;
  freq_max: number | null;
  freq_step: number | null;
  num_points: number | null;
  columns: string[] | null;
  tags: string[];
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface DatasetListResponse {
  datasets: Dataset[];
  total: number;
}

export interface AlignmentResponse {
  aligned_file_path: string;
  reference_points: number;
  target_points_original: number;
  target_points_aligned: number;
  freq_min: number;
  freq_max: number;
  freq_step: number;
  preview_data: {
    columns: string[];
    data: Record<string, number>[];
    total_rows: number;
    preview_rows: number;
  } | null;
}

// ML Model types
export interface MLModel {
  id: number;
  name: string;
  model_type: string;
  dataset_id: number;
  target_variable: string;
  feature_columns: string[];
  hyperparameters: Record<string, unknown> | null;
  mse: number | null;
  rmse: number | null;
  mae: number | null;
  r2_score: number | null;
  training_duration_seconds: number | null;
  feature_importance: Record<string, number> | null;
  training_history: Record<string, unknown> | null;
  notes: string | null;
  tags: string[];
  created_at: string;
}

export interface TrainingRequest {
  dataset_id: number;
  target_variable: string;
  feature_columns: string[];
  model_types: string[];
  test_size: number;
  name_prefix?: string;
}

export interface ModelResult {
  model_type: string;
  mse: number;
  rmse: number;
  mae: number;
  r2_score: number;
  training_duration_seconds: number;
  feature_importance: Record<string, number> | null;
  model_id: number;
}

export interface TrainingResponse {
  results: ModelResult[];
  dataset_name: string;
  target_variable: string;
  num_training_samples: number;
  num_test_samples: number;
}

export interface PredictionResponse {
  prediction: number;
  model_type: string;
  model_name: string;
  input_features: Record<string, number>;
}

// Publication types
export interface Publication {
  id: number;
  title: string;
  journal: string | null;
  status: string;
  abstract: string | null;
  highlights: string[] | null;
  dataset_ids: number[];
  model_ids: number[];
  design_ids: number[];
  tags: string[];
  notes: string | null;
  created_at: string;
}

export interface LatexTableResponse {
  latex_code: string;
  num_rows: number;
  num_cols: number;
  preview_text: string;
}

export interface HighlightsResponse {
  highlights: string[];
  latex_formatted: string;
}

// Antenna Design types
export interface AntennaDesign {
  id: number;
  name: string;
  description: string | null;
  geometry_params: Record<string, unknown> | null;
  dimensions_mm: Record<string, number> | null;
  performance: Record<string, unknown> | null;
  s11_min_db: number | null;
  peak_gain_dbi: number | null;
  bandwidth_mhz: number | null;
  frequency_band: string | null;
  antenna_type: string | null;
  substrate: string | null;
  application: string | null;
  dataset_ids: number[];
  model_ids: number[];
  paper_ids: number[];
  file_paths: string[];
  tags: string[];
  notes: string | null;
  created_at: string;
}

// Figure types
export interface FigureRequest {
  plot_type: string;
  dataset_id?: number;
  data?: Record<string, unknown>;
  title?: string;
  x_label?: string;
  y_label?: string;
  x_column?: string;
  y_columns?: string[];
  style?: string;
  width_inches?: number;
  height_inches?: number;
  dpi?: number;
  export_format?: string;
  colors?: string[];
  legend_labels?: string[];
  show_grid?: boolean;
}

// Dashboard types
export interface DashboardStats {
  stats: {
    total_datasets: number;
    total_models: number;
    total_designs: number;
    total_publications: number;
    active_papers: number;
    best_r2: number | null;
    best_model_name: string | null;
  };
  recent_datasets: {
    id: number;
    name: string;
    source: string;
    frequency_band: string | null;
    created_at: string;
  }[];
}

// Unit converter
export interface UnitConversion {
  input_value: number;
  input_unit: string;
  output_value: number;
  output_unit: string;
}
