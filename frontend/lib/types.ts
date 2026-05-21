export type Delegate = {
  id: string;
  name: string;
  country?: string | null;
  committee?: string | null;
  notes?: string | null;
  created_at: string;
  document_count: number;
};

export type DelegateProfile = {
  delegate: Delegate;
  documents: HistoryDocument[];
  embedding_stats?: EmbeddingStats | null;
  style_baseline?: Record<string, number> | null;
};

export type HistoryDocument = {
  id: string;
  filename: string;
  documentType: string;
  meeting?: string | null;
  documentDate?: string | null;
  status: string;
  errorMessage?: string | null;
  createdAt: string;
};

export type EmbeddingStats = {
  document_count: number;
  centroid: number[];
  normal_range: Record<string, number>;
  cluster_points: ClusterPoint[];
};

export type ClusterPoint = {
  label: string;
  x: number;
  y: number;
  kind: "history" | "analysis";
};

export type AnalysisResult = {
  riskLevel: string;
  historicalDeviation: number;
  stylometricShift: number;
  semanticDrift: number;
  embeddingDistance: { cosine: number; mahalanobis: number };
  significantFeatures: { feature: string; zScore: number }[];
  radar: { feature: string; baseline: number; current: number; rawBaseline: number; rawCurrent: number }[];
  featureDrift: { feature: string; zScore: number }[];
  interpretation: string;
};

export type AnalyzeResponse = {
  analysis_id: string;
  delegate_id: string;
  filename: string;
  risk_level: string;
  result: AnalysisResult;
};

