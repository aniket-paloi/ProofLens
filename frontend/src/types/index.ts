export interface Page {
  id: string;
  page_number: number;
  width_pts: number;
  height_pts: number;
  rotation_deg: number;
  has_native_text: number;
  rendered_image_url?: string;
}

export interface Document {
  id: string;
  case_id: string;
  filename: string;
  mime_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  classified_type: 'APPLICATION_FORM' | 'SALARY_SLIP' | 'BANK_STATEMENT' | 'UNKNOWN';
  classification_confidence: number;
  page_count: number;
  created_at: string;
  pages?: Page[];
}

export interface Case {
  id: string;
  reference_number: string;
  applicant_name: string;
  status: 'ACTIVE' | 'REVIEWED' | 'ARCHIVED';
  created_at: string;
  updated_at: string;
  documents?: Document[];
}

export interface FieldRevision {
  id: string;
  field_id: string;
  revision_number: number;
  actor_id: string;
  reason: string;
  previous_value: string;
  new_value: string;
  created_at: string;
}

export interface Field {
  id: string;
  run_id: string;
  page_id: string;
  field_name: string;
  raw_value: string;
  normalized_value?: string;
  numeric_value?: number;
  currency: string;
  period_start?: string;
  period_end?: string;
  bbox_normalized: [number, number, number, number]; // [ymin, xmin, ymax, xmax] in [0, 1]
  extractor_name: string;
  extractor_version: string;
  extraction_score: number;
  current_revision_num: number;
  created_at: string;
  revisions?: FieldRevision[];
}

export interface Claim {
  id: string;
  run_id: string;
  claim_type: string;
  subject: string;
  basis: string;
  amount?: number;
  currency: string;
  period_start?: string;
  period_end?: string;
  status: string;
  supporting_field_ids: string[];
}

export interface Transaction {
  id: string;
  run_id: string;
  page_id: string;
  transaction_date: string;
  narration: string;
  transaction_type: 'CREDIT' | 'DEBIT';
  amount: number;
  running_balance?: number;
  is_salary_candidate: number;
  bbox_normalized?: [number, number, number, number];
}

export interface EvidenceLink {
  id: string;
  finding_id: string;
  entity_type: string;
  entity_id: string;
  role: string;
  notes?: string;
}

export interface Finding {
  id: string;
  case_id: string;
  run_id: string;
  title: string;
  observation_type: 'CONTEXTUAL_MISMATCH' | 'VISUAL_ANOMALY' | 'TEXT_LAYER_DESYNC' | 'MISSING_COVERAGE';
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  uncertainty: 'LOW' | 'MEDIUM' | 'HIGH';
  summary: string;
  alternative_explanations: string[];
  next_recommended_checks: string[];
  reviewer_disposition: 'UNREVIEWED' | 'CONFIRMED' | 'DISMISSED' | 'FURTHER_VERIFICATION_NEEDED';
  reviewer_notes?: string;
  reviewer_actor_id?: string;
  reviewed_at?: string;
  created_at: string;
  evidence_links?: EvidenceLink[];
}

export interface CheckExecution {
  id: string;
  check_id: string;
  lifecycle_state: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  applicability: 'APPLICABLE' | 'NOT_APPLICABLE' | 'UNSUPPORTED';
  outcome: 'CONSISTENT' | 'DISCREPANCY' | 'POSSIBLE_EXPLANATION' | 'INSUFFICIENT_EVIDENCE' | 'UNABLE_TO_ASSESS';
  assumptions: string[];
  limitations?: string;
}

export interface AuditEvent {
  id: string;
  case_id: string;
  sequence_number: number;
  action_type: string;
  actor_id: string;
  payload_json: string;
  previous_event_hash: string;
  current_event_hash: string;
  created_at: string;
}

