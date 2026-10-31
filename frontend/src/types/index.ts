export interface RiskIndicator {
  id: string;
  name: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  description: string;
  evidence: string;
  rationale: string;
}

export interface SyntaxToken {
  text: string;
  type: string;
  is_suspicious: boolean;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO' | 'SAFE';
  tooltip: string;
}

export interface EmlAttachment {
  filename: string;
  content_type: string;
  size_bytes: number;
  is_executable: boolean;
}

export interface EmlMetadata {
  from_header: string;
  to_header: string;
  date_header: string;
  spf_header?: string | null;
  dkim_present: boolean;
  auth_results?: string | null;
  embedded_urls: string[];
  attachments: EmlAttachment[];
}

export interface FeatureContribution {
  feature: string;
  display_name: string;
  description: string;
  raw_value: number | string;
  contribution: number;
  direction: 'phishing' | 'legitimate';
  abs_contribution: number;
}

export interface InfluentialTerm {
  term: string;
  tfidf_value: number;
  coefficient: number;
  contribution: number;
  direction: 'phishing' | 'legitimate';
  abs_contribution: number;
}

export interface BrandImpersonation {
  is_impersonating: boolean;
  target_brand: string;
  canonical_domain: string;
  spoof_technique: string;
  severity: string;
  similarity_score: number;
  details: string;
}

export interface EnsembleModelResult {
  model_name: string;
  prediction: string;
  phishing_probability: number;
  is_phishing: boolean;
}

export interface EnsembleConsensus {
  models_evaluated: number;
  consensus_verdict: string;
  agreement_ratio: number;
  models: EnsembleModelResult[];
}

export interface UrlScanResult {
  scan_id: string;
  scan_type: 'url';
  target: string;
  defanged_target?: string;
  prediction: string;
  is_phishing: boolean;
  confidence_score: number;
  phishing_probability: number;
  risk_level: 'High' | 'Medium' | 'Low';
  risk_indicators: RiskIndicator[];
  brand_impersonation?: BrandImpersonation | null;
  ensemble_consensus?: EnsembleConsensus | null;
  feature_contributions: FeatureContribution[];
  syntax_tokens?: SyntaxToken[];
  explanation: string;
  model_version: string;
  timestamp: string;
  disclaimer: string;
}

export interface DefangResponse {
  raw_url: string;
  defanged_url: string;
  is_defanged: boolean;
  soc_shareable_snippet: string;
}

export interface CounterfactualResult {
  original_url: string;
  original_probability: number;
  original_prediction: string;
  counterfactual_probability: number;
  counterfactual_prediction: string;
  probability_delta: number;
  percent_reduction: number;
  counterfactual_risk_level: 'High' | 'Medium' | 'Low';
  verdict_flipped: boolean;
  remediated_factors: string[];
  narrative: string;
  applied_modifications: Record<string, boolean>;
}

export interface BatchUrlScanItem {
  scan_id: string;
  target: string;
  defanged_target: string;
  prediction: string;
  is_phishing: boolean;
  confidence_score: number;
  phishing_probability: number;
  risk_level: 'High' | 'Medium' | 'Low';
  target_brand?: string | null;
  top_indicator?: string | null;
}

export interface BatchSummary {
  total: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  phishing_count: number;
  legitimate_count: number;
}

export interface BatchUrlScanResult {
  summary: BatchSummary;
  results: BatchUrlScanItem[];
  timestamp: string;
}

export interface EmailScanResult {
  scan_id: string;
  scan_type: 'email';
  target_preview: string;
  prediction: string;
  is_phishing: boolean;
  confidence_score: number;
  phishing_probability: number;
  risk_level: 'High' | 'Medium' | 'Low';
  risk_indicators: RiskIndicator[];
  influential_terms: InfluentialTerm[];
  explanation: string;
  model_version: string;
  timestamp: string;
  warning: string;
  extracted_subject?: string;
  extracted_body?: string;
  eml_metadata?: EmlMetadata;
}

export interface MisclassifiedSample {
  sample_id: string;
  item_type: 'url' | 'email';
  preview: string;
  true_label: number;
  true_label_name: string;
  predicted_label: number;
  predicted_label_name: string;
  error_type: 'False Positive' | 'False Negative';
  predicted_score: number;
  reason_notes: string;
}

export interface EvaluationReport {
  model_type: string;
  model_version: string;
  algorithm: string;
  evaluated_at: string;
  dataset_summary: {
    total_records: number;
    train_records: number;
    test_records: number;
    class_distribution: {
      train_legitimate: number;
      train_phishing: number;
      test_legitimate: number;
      test_phishing: number;
    };
  };
  evaluation_protocol: string;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    false_positive_rate: number | null;
    false_negative_rate: number | null;
    confusion_matrix: {
      true_negatives: number;
      false_positives: number;
      false_negatives: number;
      true_positives: number;
      matrix_2x2: number[][];
    };
    per_class: {
      legitimate: {
        precision: number;
        recall: number;
        f1_score: number;
        support: number;
      };
      phishing: {
        precision: number;
        recall: number;
        f1_score: number;
        support: number;
      };
    };
  };
  model_comparison: Array<{
    model_name: string;
    cv_accuracy: number;
    cv_precision: number;
    cv_recall: number;
    cv_f1: number;
    test_accuracy?: number;
    test_f1?: number;
    selected?: boolean;
  }>;
  misclassified_samples: MisclassifiedSample[];
  feature_count?: number;
  vocabulary_size?: number;
}

export interface ScanStatistics {
  total_scans: number;
  phishing_scans: number;
  legitimate_scans: number;
  url_scans: number;
  email_scans: number;
  phishing_ratio: number;
}

export interface AllMetricsData {
  url_evaluation: EvaluationReport | null;
  email_evaluation: EvaluationReport | null;
  model_comparison: any;
  scan_statistics: ScanStatistics;
}

export interface HistoryItem {
  scan_id: string;
  scan_type: 'url' | 'email';
  target_preview: string;
  prediction: string;
  is_phishing: boolean;
  confidence_score: number;
  risk_level: string;
  indicators_count: number;
  model_version: string;
  created_at: string;
  details: {
    risk_indicators?: RiskIndicator[];
    feature_contributions?: FeatureContribution[];
    influential_terms?: InfluentialTerm[];
    explanation?: string;
    phishing_probability?: number;
  };
}

export interface HealthData {
  status: 'healthy' | 'degraded';
  timestamp: string;
  database_status: string;
  models_ready: boolean;
  models: {
    url_classifier: { ready: boolean; size_bytes: number };
    email_classifier: { ready: boolean; size_bytes: number };
    all_ready: boolean;
  };
}
